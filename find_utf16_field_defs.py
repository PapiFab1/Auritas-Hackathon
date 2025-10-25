import re

fn = "BC_BC_ARCHIVE_20240621_070552_0.ARCHIVE.ARCHIVE"
marker = b"4103"
data = open(fn, "rb").read()

offs=[]; pos=0
while True:
    i=data.find(marker,pos)
    if i==-1: break
    offs.append(i); pos=i+1
offs.append(len(data))

for n in range(3):    
    a,b=offs[n],offs[n+1]
    chunk=data[a:b]
    try:
        txt=chunk.decode("utf-16le","ignore")
    except:
        continue
    lines=[l for l in txt.splitlines() if "|" in l]
    if lines:
        print(f"\n✅ UTF-16 field defs in chunk {n}:")
        for l in lines[:20]:
            print(" ",l)
