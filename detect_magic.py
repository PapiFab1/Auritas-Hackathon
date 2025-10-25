import binascii

filename = "BC_BC_ARCHIVE_20240621_070552_0.ARCHIVE.ARCHIVE"

with open(filename, "rb") as f:
    data = f.read()

magics = {
    b'\x1f\x8b': 'gzip',
    b'PK\x03\x04': 'zip',
    b'\x04\x22\x4d\x18': 'lz4',
    b'\x28\xb5\x2f\xfd': 'zstd'
}

candidates = [0, 512, 1024, 2048, 4096, 8192, 16384, 32768]

for offset in candidates:
    head = data[offset:offset+8]
    hex_head = binascii.hexlify(head).decode()
    print(f"Offset {offset}: {hex_head}")
    for magic, name in magics.items():
        if head.startswith(magic):
            print(f"  ⚡ Found {name} magic at offset {offset}")

