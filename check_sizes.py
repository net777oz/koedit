#!/usr/bin/env python3
from PIL import Image
import os

for f_num in range(1, 6):
    f = '{:04d}'.format(f_num)
    for d in ['export', 'originals']:
        p = '/home/net77/koedit/{}/{}.png'.format(d, f)
        if os.path.exists(p):
            img = Image.open(p)
            print('{}/{}.png -> {}'.format(d, f, img.size))
        else:
            print('{}/{}.png -> NOT FOUND'.format(d, f))
