import zlib, binascii

fn = "BC_BC_ARCHIVE_20240621_070552_0.ARCHIVE.ARCHIVE"
marker = b'4103'
data = open(fn,'rb').read()

offsets = []
pos = 0
while True:
    i = data.find(marker, pos)
    if i == -1: break
    offsets.append(i)
    pos = i + 1

a, b = offsets[4], offsets[5]
chunk = data[a:b]
print(f"Chunk 4 size: {len(chunk)} bytes")

hdr = chunk[4:68]
print("Header (first 64 bytes):", binascii.hexlify(hdr).decode())

for start in range(8, 128, 4):
    buf = chunk[start:]
    try:
        out = zlib.decompress(buf, -15)      # raw DEFLATE
        print(f"\n✅ SUCCESS at offset {start}! decompressed {len(out)} bytes")
        print("First 200 chars of output:\n", out[:200])
        break
    except Exception as e:
        pass
else:
    print("\n❌ No zlib success in tested offsets.")
