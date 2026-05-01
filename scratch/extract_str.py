import re

def extract_strings(filename, encoding='cp949', min_length=4):
    with open(filename, 'rb') as f:
        data = f.read()
    
    strings = []
    current_str = bytearray()
    
    # We will try to decode every chunk of bytes
    # A simplistic approach is to split by null bytes or non-printable ASCII/Korean ranges
    # Actually, let's just use a sliding window or split by \x00
    
    chunks = data.split(b'\x00')
    for i, chunk in enumerate(chunks):
        if len(chunk) >= min_length:
            try:
                text = chunk.decode(encoding)
                # Keep only chunks that have at least some korean characters
                if re.search(r'[가-힣]', text):
                    strings.append((i, text))
            except UnicodeDecodeError:
                # Try Johab
                try:
                    text = chunk.decode('cp1361')
                    if re.search(r'[가-힣]', text):
                        strings.append((i, text))
                except:
                    pass
    return strings

res = extract_strings('/home/net77/koedit/scratch/gamedata/EVENT1.DAT')
if res:
    print(f"Found {len(res)} strings in EVENT1.DAT:")
    for idx, s in res[:20]:
        print(f"[{idx}]: {s}")
else:
    print("No strings found. It might be compressed (LS11) or uses a custom text encoding.")
