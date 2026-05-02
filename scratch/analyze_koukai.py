import zipfile

z = zipfile.ZipFile('/home/net77/koedit/game_data/water2.zip')
data = z.read('KOUKAI2.DAT')

target = '조안'.encode('cp949')
pos = data.find(target)

if pos != -1:
    print(f"'조안' found at byte {pos:04X}")
    # Show context around '조안'
    context = data[max(0, pos-20) : min(len(data), pos+200)]
    print(f"Context (Hex): {context.hex(' ')}")
    
    # Try to detect if it's a fixed length table
    # Look for '카탈리나' after '조안'
    target2 = '카탈리나'.encode('cp949')
    pos2 = data.find(target2, pos)
    if pos2 != -1:
        print(f"'카탈리나' found at byte {pos2:04X}")
        print(f"Difference: {pos2 - pos} bytes")
else:
    print("'조안' not found in KOUKAI2.DAT (Wait, grep said True? Check encoding)")
