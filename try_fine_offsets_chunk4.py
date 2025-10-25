import zlib

fn = "BC_BC_ARCHIVE_20240621_070552_0.ARCHIVE.ARCHIVE"
marker = b'4103'
data = open(fn,'rb').read()

offs, pos = [], 0
while True:
    i = data.find(marker, pos)
    if i == -1: break
    offs.append(i)
    pos = i + 1

a, b = offs[4], offs[5]
chunk = data[a:b]

for off in range(48, 81):  
    buf = chunk[off:]
    try:
        out = zlib.decompress(buf, -15)
        if out:
            print(f"✅ offset {off} → decompressed {len(out)} bytes")
            print("First 200 chars:", out[:200])
            break
    except:
        pass
else:
    print("No raw zlib success between 48–80; trying XOR masks...")

for key in [0x55, 0xAA]:
    masked = bytes([b ^ key for b in chunk])
    for off in range(48, 81):
        buf = masked[off:]
        try:
            out = zlib.decompress(buf, -15)
            if out:
                print(f"✅ XOR key {hex(key)} offset {off} → decompressed {len(out)} bytes")
                print("First 200 chars:", out[:200])
                break
        except:
            pass
