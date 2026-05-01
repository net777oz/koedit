import sys
import struct
import bitarray
from PIL import Image

koukai2_palette_hex = ['#000000', '#00A261', '#D34100', '#F3A261', '#0041D3', '#00A2F3', '#D361A2', '#F3E3D3']

def get_rgb_palette():
    rgb_palette = []
    for h in koukai2_palette_hex:
        rgb_palette.append((int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)))
    return rgb_palette

def encode_ls11_code(code: int) -> bitarray.bitarray:
    N = code + 2
    binary_str = bin(N)[2:] 
    mask_len = len(binary_str) - 1
    
    a = bitarray.bitarray()
    for _ in range(mask_len - 1):
        a.append(1)
    a.append(0)
    for char in binary_str[1:]:
        a.append(int(char))
    return a

def ls11_encode_data_literal(data: bytes) -> bytes:
    stream = bitarray.bitarray()
    for byte in data:
        # Dictionary map: KAO.LZW dictionary contains all 0-255 in the first 256 bytes
        # Actually wait, my literal encode assumes dictionary.index(byte)
        # For simplicity, if we don't know the exact dictionary order here, we can just use 0-255 identity dict map if we create our own fake dictionary, or we need to pass the real dict!
        pass

def image_to_npk(img: Image.Image) -> bytes:
    width, height = 64, 80
    img = img.resize((width, height)).convert('RGB')
    pal = get_rgb_palette()
    
    indexed_data = []
    for y in range(height):
        for x in range(width):
            r, g, b = img.getpixel((x, y))
            best_i = 0
            best_dist = 999999
            for i, (pr, pg, pb) in enumerate(pal):
                dist = (r-pr)**2 + (g-pg)**2 + (b-pb)**2
                if dist < best_dist:
                    best_dist = dist
                    best_i = i
            indexed_data.append(best_i)
            
    out = bytearray()
    for i in range(0, len(indexed_data), 4):
        p0, p1, p2, p3 = indexed_data[i:i+4]
        b1 = 0
        b1 |= ((p0 & 4) >> 2) << 3
        b1 |= ((p1 & 4) >> 2) << 2
        b1 |= ((p2 & 4) >> 2) << 1
        b1 |= ((p3 & 4) >> 2) << 0
        
        b2 = 0
        b2 |= ((p0 & 2) >> 1) << 7
        b2 |= ((p1 & 2) >> 1) << 6
        b2 |= ((p2 & 2) >> 1) << 5
        b2 |= ((p3 & 2) >> 1) << 4
        
        b2 |= (p0 & 1) << 3
        b2 |= (p1 & 1) << 2
        b2 |= (p2 & 1) << 1
        b2 |= (p3 & 1) << 0
        
        out.append(b1)
        out.append(b2)
        
    return bytes(out)

# We need the real dictionary of Uncharted Waters 2
def get_dict():
    with open('KAO.LZW', 'rb') as f:
        f.seek(16)
        return list(f.read(256))

def ls11_encode_data_literal(data: bytes, dictionary: list) -> bytes:
    stream = bitarray.bitarray()
    for byte in data:
        idx = dictionary.index(byte)
        stream.extend(encode_ls11_code(idx))
    return stream.tobytes()

def hack_kao():
    dictionary = get_dict()
    # load face 0001
    img = Image.open('export/0001.png')
    npk_data = image_to_npk(img)
    ls11_data = ls11_encode_data_literal(npk_data, dictionary)
    
    print(f"Original size was ~1709 bytes.")
    print(f"New NPK size: {len(npk_data)} bytes.")
    print(f"New LS11 size: {len(ls11_data)} bytes.")
    
    # Unpack the KAO.LZW to reconstruct it
    with open('KAO.LZW', 'rb') as f:
        header = f.read(272)
        # Parse old table
        f.seek(272)
        pos = 272
        data = f.read()
        
    # We will just write a new file test!
    
# test
if __name__ == '__main__':
    hack_kao()
