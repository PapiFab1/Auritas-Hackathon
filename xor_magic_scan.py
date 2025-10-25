# xor_magic_scan.py
fn = "BC_BC_ARCHIVE_20240621_070552_0.ARCHIVE.ARCHIVE"
data = open(fn,'rb').read(65536)
magics = [b'\x1f\x8b', b'PK\x03\x04', b'%PDF', b'ID3', b'RIFF', b'<?xm']
hits = []
for k in range(256):
    cand = bytes([b ^ k for b in data[:64]])
    for m in magics:
        if cand.startswith(m):
            hits.append((k, m.decode(errors='ignore'), cand[:16]))
if hits:
    print("Found possible XOR keys:")
    for h in hits:
        print(h)
else:
    print("No single-byte XOR produced known magic in first 64 bytes.")
