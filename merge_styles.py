from PIL import Image, ImageDraw, ImageFont
import os

base = '/home/net77/koedit/export/'
v1 = Image.open(base + 'v1_clean.png')
v2 = Image.open(base + 'v2_soft.png')
v3 = Image.open(base + 'v3_vivid.png')
v4 = Image.open(base + 'v4_retro.png')

w, h = v1.size
combined = Image.new('RGB', (w*2 + 20, h*2 + 20), (50, 50, 50))

# Paste with small margins
combined.paste(v1, (5, 5))
combined.paste(v2, (w + 15, 5))
combined.paste(v3, (5, h + 15))
combined.paste(v4, (w + 15, h + 15))

combined.save('/home/net77/koedit/style_comparison.png')
print("Comparison image created.")
