import sys
import os

sys.path.append('kaodata/dekoei')
from ls11 import ls11_decode_parts

def analyze_kao():
    with open('KAO.LZW', 'rb') as f:
        data = f.read()
    
    # ls11_decode_parts decodes all blocks and returns a list of bytes
    decoded = ls11_decode_parts(data)
    print(f"Total blocks decoded: {len(decoded)}")
    
    sizes = [len(b) for b in decoded]
    for i in range(min(140, len(sizes))):
        print(f"Block {i:03d}: {sizes[i]} bytes")

if __name__ == '__main__':
    analyze_kao()
