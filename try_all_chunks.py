import zlib

fn = "BC_BC_ARCHIVE_20240621_070552_0.ARCHIVE.ARCHIVE"
marker = b'4103'
data = open(fn, 'rb').read()

# find all chunks
offsets = []
pos = 0
while True:
    i = data.find(marker, pos)
    if i == -1: break
    offsets.append(i)
    pos = i + 1
offsets.append(len(data))

for n in range(len(offsets) - 1):
    a, b = offsets[n], offsets[n + 1]
    chunk = data[a:b]
    for off in range(40, 120, 4):
        try:
            out = zlib.decompress(chunk[off:], -15)
            if len(out) > 50:
                print(f"\n✅ Chunk {n} offset {off} decompressed {len(out)} bytes")
                print(out[:300])
                raise SystemExit
        except:
            continue

print("\n❌ No readable zlib data found in tested chunks.")
