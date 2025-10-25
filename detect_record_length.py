# detect_record_length.py
from collections import Counter
fn = "BC_BC_ARCHIVE_20240621_070552_0.ARCHIVE.ARCHIVE"
data = open(fn,'rb').read()
max_cand = 2048
sample_end = min(len(data), 200000)  
sample = data[:sample_end]

def score_candidate(cand):
    if cand < 16: return 0
    cnt = 0
    a = sample[0:cand]
    for i in range(1,11):
        start = i*cand
        if start + cand <= len(sample):
            b = sample[start:start+cand]
            if a == b: cnt += 1
    return cnt

results = []
for cand in range(16, max_cand+1, 16):
    sc = score_candidate(cand)
    if sc > 0:
        results.append((cand, sc))
results.sort(key=lambda x:(-x[1], x[0]))
print("Top candidates (record_length, matches):")
for r in results[:20]:
    print(r)
