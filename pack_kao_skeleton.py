import sys
import os
import struct
import bitarray
from PIL import Image

sys.path.append('kaodata/dekoei')
from utils import pack_npk, color_codes_to_palette

# Uncharted Waters 2 PC-DOS palette
koukai2_palette_hex = ['#000000', '#00A261', '#D34100', '#F3A261', '#0041D3', '#00A2F3', '#D361A2', '#F3E3D3']
def get_rgb_palette():
    rgb_palette = []
    for h in koukai2_palette_hex:
        rgb_palette.append((int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)))
    return rgb_palette

def encode_code(code: int) -> bitarray.bitarray:
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

def ls11_encode_data_literal(data: bytes, dictionary: bytes) -> bytes:
    stream = bitarray.bitarray()
    for byte in data:
        # look up the byte in the dictionary
        # the dictionary must naturally contain all 256 values
        idx = dictionary.index(byte)
        stream.extend(encode_code(idx))
    return stream.tobytes()

def read_original_kao(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    
    magic = data[:4]
    dictionary = data[16:272]
    
    pos = 272
    infos = []
    while data[pos:pos+4] != b'\x00\x00\x00\x00':
        comp = int.from_bytes(data[pos:pos+4], 'big')
        uncomp = int.from_bytes(data[pos+4:pos+8], 'big')
        offset = int.from_bytes(data[pos+8:pos+12], 'big')
        infos.append({'comp': comp, 'uncomp': uncomp, 'offset': offset})
        pos += 12
    return magic, dictionary, infos, data

def image_to_npk(img: Image.Image, width, height) -> bytes:
    # Get 8-color indices from the image.
    img = img.convert('RGB')
    pal = get_rgb_palette()
    
    indexed_data = []
    for y in range(height):
        for x in range(width):
            r, g, b = img.getpixel((x, y))
            # Find closest color in palette
            best_i = 0
            best_dist = 999999
            for i, (pr, pg, pb) in enumerate(pal):
                dist = (r-pr)**2 + (g-pg)**2 + (b-pb)**2
                if dist < best_dist:
                    best_dist = dist
                    best_i = i
            indexed_data.append(best_i)
            
    # pack_npk packs 8-bit array into 3-bit NPK planar format
    # wait, pack_npk is not in utils.py. Let's see if kaodata has an NPK encoder.
    pass

