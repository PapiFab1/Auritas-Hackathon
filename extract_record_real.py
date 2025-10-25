import zlib

fn = "BC_BC_ARCHIVE_20240621_070552_0.ARCHIVE.ARCHIVE"
marker = b"4103"
data = open(fn, "rb").read()

offs = []; pos = 0
while True:
    i = data.find(marker, pos)
    if i == -1: break
    offs.append(i)
    pos = i + 1
offs.append(len(data))

a, b = offs[4], offs[5]
chunk = data[a:b]

out = zlib.decompress(chunk[3:], -15)
print(f"✅ Decompressed {len(out)} bytes")
open("record_chunk4_full.bin", "wb").write(out)
print("Saved as record_chunk4_full.bin")
