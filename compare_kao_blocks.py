import os
import sys

sys.path.append('kaodata/dekoei')
from ls11 import ls11_decode_parts

def compare_kaos():
    with open('KAO.LZW', 'rb') as f:
        orig_data = f.read()
    with open('KAO_NEW.LZW', 'rb') as f:
        new_data = f.read()
    
    orig_blocks = ls11_decode_parts(orig_data)
    new_blocks = ls11_decode_parts(new_data)
    
    print(f"Orig blocks: {len(orig_blocks)}, New blocks: {len(new_blocks)}")
    
    for i in range(min(128, len(orig_blocks), len(new_blocks))):
        if orig_blocks[i] != new_blocks[i]:
            # Try to see if it matches a neighbor
            found_match = False
            for j in range(max(0, i-5), min(len(new_blocks), i+5)):
                if orig_blocks[i] == new_blocks[j]:
                    print(f"Original Block {i:03d} matches New Block {j:03d} !! (Shift of {j-i})")
                    found_match = True
                    break
            if not found_match:
                 print(f"Original Block {i:03d} has no nearby match in New.")

if __name__ == '__main__':
    compare_kaos()
