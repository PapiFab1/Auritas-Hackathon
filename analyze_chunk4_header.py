import struct, binascii

fn = "BC_BC_ARCHIVE_20240621_070552_0.ARCHIVE.ARCHIVE"
data = open(fn,"rb").read()
marker = b"4103"

offs=[]; pos=0
while True:
    i=data.find(marker,pos)
    if i==-1: break
    offs.append(i); pos=i+1

a,b=offs[4],offs[5]
chunk=data[a:b]

print("Chunk len",len(chunk))
for off in range(32,57,4):
    val=struct.unpack_from("<I",chunk,off)[0]
    print(f"offset {off:02d}: {val}  (0x{val:08x})")
