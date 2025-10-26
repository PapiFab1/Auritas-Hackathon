import gzip
import lz4.frame
import os

# Step 1: Detect the compression type
def detect_compression(file_path):
    with open(file_path, 'rb') as f:
        magic = f.read(4)
    
    if magic[:2] == b'\x1f\x8b':
        return 'gzip'
    elif magic == b'\x04\x22\x4d\x18':
        return 'lz4'
    elif magic == b'\x28\xb5\x2f\xfd':
        return 'zstd'
    else:
        return 'unknown'

# Step 2: Try to decompress the file
def decompress_file(file_path):
    compression = detect_compression(file_path)
    print(f"Detected compression: {compression}")

    with open(file_path, 'rb') as f:
        data = f.read()
    
    # SAP archive files sometimes include extra metadata in the header
    # So we try skipping a few kilobytes at a time
    for skip in [0, 2048, 4096, 8192]:
        try:
            if compression == 'gzip':
                decompressed = gzip.decompress(data[skip:])
            elif compression == 'lz4':
                decompressed = lz4.frame.decompress(data[skip:])
            else:
                print("❌ Unsupported or unknown compression type.")
                return None

            print(f"✅ Success! Decompressed at offset {skip}, size = {len(decompressed)} bytes")

            # Save output to results folder
            os.makedirs("results", exist_ok=True)
            with open("results/decompressed.bin", "wb") as out:
                out.write(decompressed)

            return decompressed

        except Exception as e:
            print(f"Failed at offset {skip}: {e}")
            continue

    print("❌ Could not decompress with known offsets.")
    return None

# Test it!
if __name__ == "__main__":
    # Change this path to your real file
    file_path = r"algorithms\samples\BC_BC_ARCHIVE_20240621_070552_0.ARCHIVE.ARCHIVE"

    decompressed = decompress_file(file_path)
    if decompressed:
        print("First 200 bytes (preview):")
        print(decompressed[:200])
