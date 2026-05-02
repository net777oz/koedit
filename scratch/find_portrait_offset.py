import zipfile

z = zipfile.ZipFile('/home/net77/koedit/game_data/water2.zip')
data = z.read('KOUKAI2.DAT')

# We'll check the first 128 character entries
start_off = 0x06A9 # This is the offset of Joan's FIRST NAME
entry_size = 50

print("Analyzing first 10 character entries for Portrait ID patterns:")
for i in range(10):
    base = start_off + (i * entry_size)
    # The name is at 'base'. Let's look at bytes just BEFORE the name.
    # We suspect the portrait ID is around base-2 or base-1.
    prefix = data[base-10:base]
    name_chunk = data[base:base+13].split(b'\x00')[0]
    try:
        name = name_chunk.decode('cp949')
        print(f"Entry {i:2}: Name='{name:8}', Prefix Hex='{prefix.hex(' ')}'")
    except:
        print(f"Entry {i:2}: [Decode Error], Prefix Hex='{prefix.hex(' ')}'")

# Let's search for some specific known characters to confirm
def find_char(name_str):
    target = name_str.encode('cp949')
    pos = data.find(target)
    if pos != -1:
        # Calculate its relative index to the start_off
        rel = (pos - start_off) // entry_size
        actual_base = start_off + (rel * entry_size)
        portrait_byte = data[actual_base - 2] # Test hypothesis: offset -2
        print(f"Target '{name_str}' found at index {rel}. Byte at base-2: {portrait_byte:02X}")
    else:
        print(f"Target '{name_str}' not found")

print("\nTesting Portrait ID Hypothesis (offset -2):")
find_char('조안')
find_char('카탈리나')
find_char('오토') # Should be 02 (ID 3)
find_char('에르네스트') # Should be 03 (ID 4)
