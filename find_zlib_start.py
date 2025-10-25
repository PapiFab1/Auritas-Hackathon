fn = "BC_BC_ARCHIVE_20240621_070552_0.ARCHIVE.ARCHIVE"
import zlib

data = open(fn, "rb").read()
marker = b"4103"
offs=[]; pos=0
while True:
    i=data.find(marker,pos)
    if i==-1: break
    offs.append(i); pos=i+1
offs.append(len(data))

a,b=offs[4],offs[5]
chunk=data[a:b]

for off in range(0,200):
    try:
        zlib.decompress(chunk[off:], -15)
        print(f"✅ valid zlib start at offset {off}")
        break
    except zlib.error:
        continue
else:
    print("❌ no valid zlib header found in first 200 bytes")
