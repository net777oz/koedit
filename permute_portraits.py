#!/usr/bin/env python3
import os
import shutil
import tempfile
from PIL import Image

BASE_DIR = '/home/net77/koedit'
ORIGINALS = os.path.join(BASE_DIR, 'originals')
EXPORT = os.path.join(BASE_DIR, 'export')

print('Step 1: Restoring originals to export...')
restored = 0
for i in range(1, 129):
    fn = '{:04d}.png'.format(i)
    src = os.path.join(ORIGINALS, fn)
    dst = os.path.join(EXPORT, fn)
    if os.path.exists(src):
        shutil.copy2(src, dst)
        restored += 1
    else:
        print('  WARNING: {} not found'.format(src))
print('  Restored {} files'.format(restored))

tmpdir = tempfile.mkdtemp(prefix='permute_', dir=BASE_DIR)
print('Step 2: Copying originals to temp dir...')
for i in range(1, 129):
    fn = '{:04d}.png'.format(i)
    src = os.path.join(ORIGINALS, fn)
    if os.path.exists(src):
        shutil.copy2(src, os.path.join(tmpdir, fn))

print('Step 3: Permuting (shift by +1)...')
permuted = 0
for i in range(1, 129):
    src_slot = i - 1 if i > 1 else 128
    src_fn = '{:04d}.png'.format(src_slot)
    dst_fn = '{:04d}.png'.format(i)
    src = os.path.join(tmpdir, src_fn)
    dst = os.path.join(EXPORT, dst_fn)
    if os.path.exists(src):
        shutil.copy2(src, dst)
        permuted += 1
    else:
        print('  WARNING: src slot {} not found for target {}'.format(src_slot, i))
print('  Permuted {} files'.format(permuted))

shutil.rmtree(tmpdir)

print()
print('Verification (export sizes):')
for i in [1, 2, 3, 64, 128]:
    p = os.path.join(EXPORT, '{:04d}.png'.format(i))
    if os.path.exists(p):
        img = Image.open(p)
        print('  {:04d}.png -> {}'.format(i, img.size))

print()
print('Done! All portraits shifted by 1 position.')
print('Slot 1 now has the portrait of original slot 128')
print('Slot 2 now has the portrait of original slot 1')