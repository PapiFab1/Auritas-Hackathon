def detect_compression(file_path):
    with open(file_path, 'rb') as f:
        magic = f.read(4)
    
    if magic[:2] == b'\x1f\x8b':
        return 'gzip'
    elif magic == b'\x04\x22\x4d\x18':
        return 'lz4'
    elif magic == b'\x28\xb5\x2f\xfd':
        return 'zstd'
    else:
        return 'unknown'

# Test it!
print(detect_compression('put path url'))

