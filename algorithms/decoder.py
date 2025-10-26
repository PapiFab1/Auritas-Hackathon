import gzip
import lz4.frame
import zstandard as zstd  # in case SAP uses zstd
import zlib
import os
import string
import time
import json


os.makedirs("results", exist_ok=True)



# Step 1: Detect compression by scanning for magic bytes
def find_magic_offset(file_path):
    """
    Scan the file for known compression magic bytes.
    Returns a tuple: (compression_type, offset)
    """
    signatures = {
        b'\x1f\x8b': 'gzip',
        b'\x04\x22\x4d\x18': 'lz4',
        b'\x28\xb5\x2f\xfd': 'zstd'
    }

    with open(file_path, 'rb') as f:
        data = f.read()

    for sig, comp_type in signatures.items():
        index = data.find(sig)
        if index != -1:
            print(f"Found {comp_type} signature at offset {index} bytes.")
            return comp_type, index

    print("No known compression signature found.")
    return None, None

# Step X: Detect possible zlib-compressed sub-blocks inside the file
def find_zlib_blocks(file_path):
    """
    Scan the file for possible zlib-compressed regions.
    SAP sometimes embeds zlib streams without a standard gzip header.
    """
    with open(file_path, 'rb') as f:
        data = f.read()

    for i in range(0, len(data) - 4):
        if data[i] == 0x78:  # zlib headers often start with 0x78
            try:
                test = zlib.decompress(data[i:])
                print(f"Possible zlib stream found at offset {i}, size {len(test)} bytes.")
                # Optionally save decompressed data for inspection
                with open("results/zlib_output.bin", "wb") as out:
                    out.write(test)
                return test
            except:
                continue

    print("No zlib-compressed blocks found.")
    return None

# Step Y: Scan for SAP ADK-style segments
def scan_segments(file_path):
    """
    Scans binary data for ADK-style [2-byte ID][4-byte length] segment patterns
    and automatically extracts each segment.
    """
    with open(file_path, 'rb') as f:
        data = f.read()

    i = 0
    print("Scanning file for possible ADK segments...")
    while i < len(data) - 6:
        seg_id = int.from_bytes(data[i:i+2], 'big')
        seg_len = int.from_bytes(data[i+2:i+6], 'big')

        if 10 <= seg_len <= 1_000_000:
            print(f"Segment ID: {seg_id:04X}, Length: {seg_len} bytes, Offset: {i}")
            # Extract segment automatically
            output_file = extract_segment(file_path, i, 6 + seg_len)
            extract_ascii_from_bin(output_file)
            detect_repeating_patterns(output_file)

            i += 6 + seg_len
        else:
            i += 1

# Step Z: Extract any discovered ADK segment
def extract_segment(file_path, offset, length):
    """
    Extracts a specific segment from the archive file and saves it as a separate .bin file.
    """
    with open(file_path, 'rb') as f:
        f.seek(offset)
        segment = f.read(length)

    output_name = os.path.join("results", f"segment_{offset}.bin")
    with open(output_name, "wb") as out:
        out.write(segment)

    print(f"Saved {output_name} ({length} bytes)")
    return output_name  # Make sure this is the LAST LINE


def extract_ascii_from_bin(file_path, min_length=4):
    """
    Scans a binary file and extracts readable ASCII text sequences.
    Saves them to a .txt file in the results/ folder.
    """
    with open(file_path, 'rb') as f:
        data = f.read()

    printable = set(bytes(string.printable, 'ascii'))
    current = bytearray()
    results = []

    for b in data:
        if b in printable:
            current.append(b)
        else:
            if len(current) >= min_length:
                results.append(current.decode('ascii'))
            current = bytearray()

    # handle last sequence
    if len(current) >= min_length:
        results.append(current.decode('ascii'))

    # Save to file
    output_name = os.path.join("results", os.path.basename(file_path) + "_ascii.txt")
    with open(output_name, "w", encoding="utf-8") as out:
        out.write("\n".join(results))

    print(f"Extracted {len(results)} text sequences from {file_path}")
    print(f"Saved to {output_name}")
    return output_name

def detect_repeating_patterns(file_path, window=16, limit=200000):
    """
    Scans the binary file for repeating fixed-size patterns to guess record length.
    """
    with open(file_path, 'rb') as f:
        data = f.read(limit)

    print(f"Analyzing first {len(data)} bytes of {file_path} for repeating patterns...")

    # try window sizes 8-256 bytes
    scores = {}
    for w in range(8, 257, 8):
        matches = sum(1 for i in range(0, len(data)-w, w)
                      if data[i:i+8] == data[i+w:i+w+8])
        scores[w] = matches

    likely = max(scores, key=scores.get)
    print(f"Most likely repeating block size: {likely} bytes (possible record length).")
    return likely

def guess_fields(record_bytes):
    """
    Heuristically guess fields within one record.
    Returns a list of (offset, length, type, value)
    """
    import re
    fields = []
    i = 0
    while i < len(record_bytes):
        chunk = record_bytes[i:i+16]  # small scan window
        ascii_text = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)

        # Heuristics
        if re.match(r'[A-Z0-9]{4,}', ascii_text.strip()):
            ftype = "CHAR"
            flen = len(chunk)
        elif re.match(r'\d{8}', ascii_text.strip()):
            ftype = "DATE"
            flen = 8
        elif chunk[-1] in (0x0C, 0x0D, 0x0F):  # packed decimal
            ftype = "PACKED"
            flen = len(chunk)
        else:
            ftype = "BIN"
            flen = len(chunk)

        fields.append({
            'offset': i,
            'length': flen,
            'type': ftype,
            'preview': ascii_text
        })
        i += flen
    return fields

def parse_record_fields(record_bytes, field_defs):
    """Use the guessed or known field definitions to decode one record."""
    record = {}
    for f in field_defs:
        start, length, ftype = f['offset'], f['length'], f['type']
        field_data = record_bytes[start:start+length]

        if ftype == 'CHAR':
            value = field_data.decode('utf-8', errors='ignore').strip()
        elif ftype == 'DATE':
            s = field_data.decode('ascii', errors='ignore')
            value = f"{s[0:4]}-{s[4:6]}-{s[6:8]}" if len(s) == 8 else s
        elif ftype == 'PACKED':
            value = parse_packed(field_data, decimals=2)
        else:
            value = field_data.hex()
        record[f"F_{start:03}"] = value
    return record



# Step 2: Decompress File (based on magic offset)
def decompress_file(file_path):
    compression, offset = find_magic_offset(file_path)

    if compression and offset is not None:
        with open(file_path, 'rb') as f:
            data = f.read()
            compressed_data = data[offset:]
            try:
                if compression == 'gzip':
                    result = gzip.decompress(compressed_data)
                elif compression == 'lz4':
                    result = lz4.frame.decompress(compressed_data)
                elif compression == 'zstd':
                    dctx = zstd.ZstdDecompressor()
                    result = dctx.decompress(compressed_data)
                print(f"Successfully decompressed with {compression}! Size: {len(result)} bytes.")
                return result
            except Exception as e:
                print(f"Failed to decompress with {compression}: {e}")
    else:
        print("No valid compression signature detected.")

    return None


# Step 3: Find Field Definitions
def find_fields(data):
    header = data[:8192].decode('utf-8', errors='ignore')

    fields = []
    for line in header.split('\n'):
        if '|' in line:
            parts = line.split('|')
            if len(parts) >= 3:
                fields.append({
                    'name': parts[0].strip(),
                    'type': parts[1].strip(),
                    'length': int(parts[2]) if parts[2].isdigit() else 10
                })
    return fields


# Step 4: Field Parsers
def parse_char(data):
    return data.decode('utf-8', errors='ignore').strip()

def parse_date(data):
    s = data.decode('ascii', errors='ignore')
    if len(s) == 8:
        return f"{s[0:4]}-{s[4:6]}-{s[6:8]}"
    return None

def parse_int(data):
    try:
        return int.from_bytes(data[:4], 'big')
    except:
        return int.from_bytes(data[:4], 'little')


# Step 5: Main entry point
if __name__ == "__main__":
    import glob
    import time
    import json

    base_dir = r"algorithms\samples"
    all_files = sorted(glob.glob(os.path.join(base_dir, "*")))
    # Filter out folders or non-binary files (e.g., .png, .txt)
    all_files = [f for f in all_files if os.path.isfile(f) and not f.lower().endswith((".png", ".txt", ".json"))]


    if not all_files:
        print(f"No .ARCHIVE files found in {base_dir}")
        exit(0)

    print(f"Found {len(all_files)} archive files to process:\n")
    for f in all_files:
        print(f"   • {os.path.basename(f)}")
    print()

    overall_results = []
    total_start = time.time()

    for idx, file_path in enumerate(all_files, start=1):
        print("\n" + "="*70)
        print(f"Processing file {idx}/{len(all_files)}: {os.path.basename(file_path)}")
        print("="*70)

        start_time = time.time()
        data = b""
        decompressed = decompress_file(file_path)

        if decompressed is not None:
            data = decompressed
        else:
            zlib_data = find_zlib_blocks(file_path)
            if zlib_data is not None:
                data = zlib_data
            else:
                scan_segments(file_path)
                latest_segment = max(
                    (os.path.join("results", f) for f in os.listdir("results") if f.endswith(".bin")),
                    key=os.path.getctime,
                    default=None
                )
                if latest_segment:
                    with open(latest_segment, "rb") as f:
                        data = f.read()

        if len(data) == 0:
            print(f"No valid data found for {os.path.basename(file_path)} — skipping.")
            continue

        record_len = 16
        num_records = len(data) // record_len

        parsed_records = []
        for i in range(min(num_records, 20)):
            start = i * record_len
            rec = data[start:start+record_len]
            guessed = guess_fields(rec)
            parsed = parse_record_fields(rec, guessed)
            parsed_records.append(parsed)

        elapsed = time.time() - start_time
        records_per_sec = num_records / elapsed if elapsed > 0 else 0

        file_result = {
            "filename": os.path.basename(file_path),
            "size_bytes": len(data),
            "record_length": record_len,
            "record_count": num_records,
            "parsed_samples": parsed_records,
            "elapsed_time_sec": round(elapsed, 3),
            "records_per_sec": round(records_per_sec, 3),
        }

        json_path = os.path.join("results", f"decoded_output_{idx}.json")
        with open(json_path, "w", encoding="utf-8") as out:
            json.dump(file_result, out, indent=2, ensure_ascii=False)

        print(f"Results saved to {json_path}")
        print(f"Parsed {num_records} records in {elapsed:.2f}s ({records_per_sec:.1f}/sec)")
        overall_results.append(file_result)

    total_elapsed = time.time() - total_start

    # Save global summary
    summary = {
        "total_files": len(overall_results),
        "total_runtime_sec": round(total_elapsed, 2),
        "average_speed_records_per_sec": round(
            sum(r["records_per_sec"] for r in overall_results) / max(1, len(overall_results)), 2
        ),
        "total_records_parsed": sum(r["record_count"] for r in overall_results),
        "files_processed": overall_results
    }

    summary_path = os.path.join("results", "summary_all_files.json")
    with open(summary_path, "w", encoding="utf-8") as out:
        json.dump(summary, out, indent=2, ensure_ascii=False)

    print("\nALL FILES COMPLETE")
    print(f"Processed {len(overall_results)} files in {total_elapsed:.2f} seconds")
    print(f"Total records parsed: {summary['total_records_parsed']:,}")
    print(f"Summary report: {summary_path}")