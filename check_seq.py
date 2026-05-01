import os

def check_sequential_offsets():
    with open('KAO.LZW', 'rb') as f:
        data = f.read()
    
    pos = 272
    infos = []
    while data[pos:pos+4] != b'\x00\x00\x00\x00':
        comp = int.from_bytes(data[pos:pos+4], 'big')
        uncomp = int.from_bytes(data[pos+4:pos+8], 'big')
        offset = int.from_bytes(data[pos+8:pos+12], 'big')
        infos.append({'comp': comp, 'uncomp': uncomp, 'offset': offset})
        pos += 12
        if len(infos) > 0 and pos >= infos[0]['offset']:
            break

    last_offset = 0
    consistent = True
    for i, info in enumerate(infos):
        if info['offset'] < last_offset:
            print(f"Non-sequential offset at index {i}: {info['offset']} < {last_offset}")
            consistent = False
        last_offset = info['offset'] + info['comp']
    
    if consistent:
        print("All offsets are sequential.")

if __name__ == '__main__':
    check_sequential_offsets()
