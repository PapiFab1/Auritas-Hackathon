import binascii
fn="BC_BC_ARCHIVE_20240621_070552_0.ARCHIVE.ARCHIVE"
marker=b"4103"
data=open(fn,"rb").read()

offs=[];pos=0
while True:
    i=data.find(marker,pos)
    if i==-1:break
    offs.append(i);pos=i+1
a,b=offs[4],offs[5]
chunk=data[a:b]

print(f"Chunk 4 length {len(chunk)} bytes\n")
for i in range(0,256,16):
    seg=chunk[i:i+16]
    hexs=binascii.hexlify(seg).decode()
    asc="".join(chr(c) if 32<=c<127 else "." for c in seg)
    print(f"{i:04x}: {hexs:<48} {asc}")
