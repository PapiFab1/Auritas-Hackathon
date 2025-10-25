import zlib

fn = "BC_BC_ARCHIVE_20240621_070552_0.ARCHIVE.ARCHIVE"
marker = b"4103"
data = open(fn, "rb").read()

# find chunk boundaries
offs=[]; pos=0
while True:
    i=data.find(marker,pos)
    if i==-1: break
    offs.append(i); pos=i+1
offs.append(len(data))

for idx in range(len(offs)-1):
    a,b = offs[idx], offs[idx+1]
    chunk = data[a:b]
    for off in range(0,200):
        try:
            out = zlib.decompress(chunk[off:], -15)
            if len(out) > 50:
                print(f"✅ Chunk {idx} offset {off} → {len(out)} bytes")
                print(out[:200])
                break
        except zlib.error:
            continue
