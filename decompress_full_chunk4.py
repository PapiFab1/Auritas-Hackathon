import zlib, binascii

fn = "BC_BC_ARCHIVE_20240621_070552_0.ARCHIVE.ARCHIVE"
marker = b'4103'
data = open(fn,'rb').read()

offsets = []
pos = 0
while True:
    i = data.find(marker, pos)
    if i == -1:
        break
    offsets.append(i)
    pos = i + 1

a, b = offsets[4], offsets[5]
chunk = data[a:b]

print(f"Chunk 4 length: {len(chunk)} bytes")

try:
    out = zlib.decompress(chunk[56:], -15)
    print(f"✅ Decompressed {len(out)} bytes")
    print('First 500 chars of output:\n', out[:500])
except Exception as e:
    print('❌ Failed to decompress full payload:', e)

