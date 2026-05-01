import sys
import os
import struct
import bitarray
from PIL import Image

sys.path.append('kaodata/dekoei')
from utils import color_codes_to_palette

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

def image_to_3bpp_planar(img: Image.Image) -> bytes:
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
            
    # pack 8 indices into 3 bytes
    out = bytearray()
    for i in range(0, len(indexed_data), 8):
        pixels = indexed_data[i:i+8]
        g0 = g1 = g2 = 0
        for b_idx in range(8):
            p = pixels[b_idx]
            g0 |= ((p >> 2) & 1) << (7 - b_idx)
            g1 |= ((p >> 1) & 1) << (7 - b_idx)
            g2 |= ((p >> 0) & 1) << (7 - b_idx)
        out.append(g0)
        out.append(g1)
        out.append(g2)
        
    return bytes(out)

def get_dict(filename):
    with open(filename, 'rb') as f:
        f.seek(16)
        return list(f.read(256))

def ls11_encode_data_literal(data: bytes, dictionary: list) -> bytes:
    stream = bitarray.bitarray()
    for byte in data:
        idx = dictionary.index(byte)
        stream.extend(encode_ls11_code(idx))
    return stream.tobytes()

def read_original_kao(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    
    magic = data[:4]
    dictionary = list(data[16:272])
    
    pos = 272
    infos = []
    # Find End of table
    # The table ends either with 00000000 or when offset is reached.
    while pos < len(data):
        if data[pos:pos+4] == b'\x00\x00\x00\x00':
             break
        comp = int.from_bytes(data[pos:pos+4], 'big')
        uncomp = int.from_bytes(data[pos+4:pos+8], 'big')
        offset = int.from_bytes(data[pos+8:pos+12], 'big')
        
        # Stop heuristically if the values don't make sense (for example, if table ends abruptly or it overlaps data)
        # However, data starts at offset. So we should not read past the first offset.
        if len(infos) > 0 and pos >= infos[0]['offset']:
             break
             
        infos.append({'comp': comp, 'uncomp': uncomp, 'offset': offset, 'pos': pos})
        pos += 12
        
    return magic, dictionary, infos, data

if __name__ == '__main__':
    img = Image.open('export/0001.png')
    planar = image_to_3bpp_planar(img)
    dictionary = get_dict('KAO.LZW')
    ls11_data = ls11_encode_data_literal(planar, dictionary)
    print(f"Planar size: {len(planar)} bytes")
    print(f"LS11 size: {len(ls11_data)} bytes")
