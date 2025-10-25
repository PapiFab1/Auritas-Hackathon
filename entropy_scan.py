# entropy_scan.py
import math
fn = "BC_BC_ARCHIVE_20240621_070552_0.ARCHIVE.ARCHIVE"
data = open(fn,'rb').read()
def entropy(b):
    if not b: return 0.0
    counts = [0]*256
    for x in b: counts[x]+=1
    ent = 0.0
    ln = len(b)
    for c in counts:
        if c:
            p = c/ln
            ent -= p * math.log2(p)
    return ent

winsz = 4096
step = 2048
print("offset\tent")
for off in range(0, min(len(data), 200000), step):
    e = entropy(data[off:off+winsz])
    print(f"{off}\t{e:.3f}")
