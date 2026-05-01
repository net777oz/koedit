import struct

def analyze():
    with open('KAO.LZW', 'rb') as f:
        data = f.read()

    print(f"File size: {len(data)}")
    print(f"Signature: {data[:4]}")
    
    # Are there multiple files? Many Koei files contain offset tables
    # if it's multiple LS11 files packed together.
    # But KAO.LZW usually has multiple characters. 
    # Usually it's an archive containing multiple images.
    
    # Let's check for multiple 'LS11' signatures
    ls11_indices = []
    for i in range(len(data) - 4):
        if data[i:i+4] == b'LS11':
            ls11_indices.append(i)
            
    print(f"Found {len(ls11_indices)} 'LS11' signatures.")
    if len(ls11_indices) > 0:
        print(f"First 5 indices: {ls11_indices[:5]}")

if __name__ == '__main__':
    analyze()
