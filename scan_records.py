import re
fn = "BC_BC_ARCHIVE_20240621_070552_0.ARCHIVE.ARCHIVE"
data = open(fn,"rb").read()
marker=b"4103"
offs=[];pos=0
while True:
    i=data.find(marker,pos)
    if i==-1:break
    offs.append(i);pos=i+1
offs.append(len(data))
for n in range(3,9):
    a,b=offs[n],offs[n+1]
    chunk=data[a:b]
    for enc in ["utf-8","utf-16le"]:
        txt=chunk.decode(enc,"ignore")
        if "|" in txt:
            print(f"✅ chunk {n} ({enc}) lines with '|':")
            for l in txt.splitlines():
                if "|" in l: print(" ",l)
            print()
            break
