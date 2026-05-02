import zipfile

z = zipfile.ZipFile('/home/net77/koedit/game_data/water2.zip')
data = z.read('NAME.TBL')

names_to_find = ['조안', '카탈리나', '오토', '에르네스트', '피에트로', '알리', '로코', '한스']

for name in names_to_find:
    try:
        target = name.encode('cp949')
        pos = data.find(target)
        if pos != -1:
            index = pos // 13
            rem = pos % 13
            print(f"'{name}' found at index {index} (byte {pos}, remainder {rem})")
        else:
            print(f"'{name}' not found")
    except Exception as e:
        print(f"Error searching for {name}: {e}")

# Also print the first few names interpreted as CP949
print("\nFirst 20 names in NAME.TBL:")
for i in range(20):
    start = i * 13
    chunk = data[start:start+13].split(b'\x00')[0]
    try:
        print(f"{i:3}: {chunk.decode('cp949')}")
    except:
        print(f"{i:3}: [Binary {chunk.hex(' ')}]")
