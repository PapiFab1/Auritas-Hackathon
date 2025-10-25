import zlib

fn = "BC_BC_ARCHIVE_20240621_070552_0.ARCHIVE.ARCHIVE"
data = open(fn,"rb").read()
marker = b"4103"

offs=[];pos=0
while True:
    i=data.find(marker,pos)
    if i==-1:break
    offs.append(i);pos=i+1
offs.append(len(data))

a,b=offs[4],offs[5]
chunk=data[a:b]
out=zlib.decompress(chunk[72:],-15)
print(f"Decompressed {len(out)} bytes")
open("record_chunk4.bin","wb").write(out)
