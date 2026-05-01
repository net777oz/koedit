import struct

def inspect_table():
    with open('KAO.LZW', 'rb') as f:
        data = f.read(512)
    
    print(f"Header (16 bytes): {data[:16].hex(' ')}")
    print(f"Dictionary starts at 16, first 8 bytes: {data[16:24].hex(' ')}")
    
    # Let's find where the first block offset is mentioned
    # The table search in ls11.py starts at 272
    pos = 272
    comp = int.from_bytes(data[pos:pos+4], 'big')
    uncomp = int.from_bytes(data[pos+4:pos+8], 'big')
    offset = int.from_bytes(data[pos+8:pos+12], 'big')
    print(f"First entry at {pos}: comp={comp}, uncomp={uncomp}, offset={offset} ({hex(offset)})")
    
    # What's at 272 - 12?
    pos2 = 272 - 12
    comp2 = int.from_bytes(data[pos2:pos2+4], 'big')
    uncomp2 = int.from_bytes(data[pos2+4:pos2+8], 'big')
    offset2 = int.from_bytes(data[pos2+8:pos2+12], 'big')
    print(f"Entry at {pos2}: comp={comp2}, uncomp={uncomp2}, offset={offset2} ({hex(offset2)})")

if __name__ == '__main__':
    inspect_table()
