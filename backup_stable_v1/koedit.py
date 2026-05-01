#!/usr/bin/env python3
import sys, os, struct, bitarray
from PIL import Image
koukai2_palette_hex = ['#000000', '#00A261', '#D34100', '#F3A261', '#0041D3', '#00A2F3', '#D361A2', '#F3E3D3']
def get_rgb_palette(): return [(int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)) for h in koukai2_palette_hex]
def encode_ls11_code(code: int) -> bitarray.bitarray:
    N = code + 2; bs = bin(N)[2:]; ml = len(bs) - 1; a = bitarray.bitarray()
    for _ in range(ml - 1): a.append(1)
    a.append(0); [a.append(int(c)) for c in bs[1:]]; return a
def image_to_3bpp_planar(img: Image.Image) -> bytes:
    img = img.resize((64, 80)).convert('RGB'); pal = get_rgb_palette(); idxs = []
    for y in range(80):
        for x in range(64):
            r, g, b = img.getpixel((x, y)); bi, bd = 0, 999999
            for i, (pr, pg, pb) in enumerate(pal):
                d = (r-pr)**2 + (g-pg)**2 + (b-pb)**2
                if d < bd: bd, bi = d, i
            idxs.append(bi)
    out = bytearray()
    for i in range(0, len(idxs), 8):
        pxs = idxs[i:i+8]; g0, g1, g2 = 0, 0, 0
        for b_idx in range(8):
            p = pxs[b_idx]; g0 |= ((p >> 2) & 1) << (7 - b_idx); g1 |= ((p >> 1) & 1) << (7 - b_idx); g2 |= ((p >> 0) & 1) << (7 - b_idx)
        out.extend([g0, g1, g2])
    return bytes(out)
def ls11_encode_data_literal(data, dic):
    s = bitarray.bitarray()
    for b in data: s.extend(encode_ls11_code(dic.index(b)))
    return s.tobytes()
def pack_kao(in_dir, orig, out_fn):
    with open(orig, 'rb') as f: d = f.read()
    dic = list(d[16:272]); pos, infos = 272, []
    while pos < len(d):
        if d[pos:pos+4] == b'\x00\x00\x00\x00': break
        c, u, o = struct.unpack('>III', d[pos:pos+12])
        if infos and pos >= infos[0]['o']: break
        infos.append({'c': c, 'u': u, 'o': o}); pos += 12
    chunks = [d[i['o']:i['o']+i['c']] for i in infos]
    for i in range(len(infos)):
        p = os.path.join(in_dir, f'{i+1:04d}.png')
        if os.path.exists(p):
            img = Image.open(p); pl = image_to_3bpp_planar(img); ls = ls11_encode_data_literal(pl, dic)
            infos[i]['c'], infos[i]['u'], chunks[i] = len(ls), len(pl), ls
    ot, od = bytearray(), bytearray(); cur = 272 + len(infos) * 12 + 4
    for i, info in enumerate(infos):
        ot.extend(struct.pack('>III', info['c'], info['u'], cur))
        od.extend(chunks[i]); cur += info['c']
    ot.extend(b'\x00\x00\x00\x00')
    with open(out_fn, 'wb') as f: f.write(d[:272]); f.write(ot); f.write(od)
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'pack': pack_kao('export', 'KAO.LZW', 'KAO_NEW.LZW')
