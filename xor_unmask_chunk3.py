import zlib

fn = "BC_BC_ARCHIVE_20240621_070552_0.ARCHIVE.ARCHIVE"
marker = b'4103'
data = open(fn, 'rb').read()

offsets, pos = [], 0
while True:
    i = data.find(marker, pos)
    if i == -1: break
    offsets.append(i)
    pos = i + 1
a, b = offsets[3], offsets[4]
chunk = data[a:b]

for key in [0x55, 0xAA, 0xFF, 0x33]:
    masked = bytes([x ^ key for x in chunk])
    for off in range(60, 100):
        try:
            out = zlib.decompress(masked[off:], -15)
            if len(out) > 50:
                print(f"✅ XOR key {hex(key)} offset {off} → {len(out)} bytes")
                print(out[:400])
                raise SystemExit
        except:
            continue

print("❌ No readable zlib stream after XOR masking.")
