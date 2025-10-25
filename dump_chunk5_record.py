import zlib, binascii
fn="BC_BC_ARCHIVE_20240621_070552_0.ARCHIVE.ARCHIVE"
marker=b"4103"
data=open(fn,"rb").read()

offs=[]; pos=0
while True:
    i=data.find(marker,pos)
    if i==-1: break
    offs.append(i); pos=i+1
offs.append(len(data))

a,b=offs[5],offs[6]
chunk=data[a:b]
out=zlib.decompress(chunk[15:],-15)
open("record_chunk5.bin","wb").write(out)
print(f"Saved record_chunk5.bin ({len(out)} bytes)")
# quick preview
for i in range(0,128,16):
    seg=out[i:i+16]
    hexs=binascii.hexlify(seg).decode()
    asc="".join(chr(c) if 32<=c<127 else "." for c in seg)
    print(f"{i:04x}: {hexs:<48} {asc}")
