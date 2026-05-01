import zipfile
import re

zip_path = '/home/net77/koedit/web_client/game/water2.zip'

def extract_strings_from_zip(filename, encoding='cp949', min_length=4):
    with zipfile.ZipFile(zip_path, 'r') as z:
        data = z.read(filename)
    
    strings = []
    chunks = data.split(b'\x00')
    for i, chunk in enumerate(chunks):
        if len(chunk) >= min_length:
            try:
                text = chunk.decode(encoding)
                if re.search(r'[가-힣]', text):
                    strings.append((i, text))
            except UnicodeDecodeError:
                pass
    return strings

res = extract_strings_from_zip('SNR1.DAT')
if res:
    print(f"Found {len(res)} strings in SNR1.DAT:")
    for idx, s in res[:20]:
        print(f"[{idx}]: {s}")
else:
    print("No strings found in SNR1.DAT.")
