import struct

def dump_messages(dat_file, out_file):
    with open(dat_file, 'rb') as f:
        data = f.read()
    
    first_offset = struct.unpack('>H', data[0:2])[0]
    num_messages = first_offset // 2
    
    offsets = []
    for i in range(num_messages):
        offset = struct.unpack('>H', data[i*2:i*2+2])[0]
        offsets.append(offset)
    offsets.append(len(data))
    
    with open(out_file, 'w', encoding='utf-8') as out:
        for i in range(num_messages):
            start = offsets[i]
            end = offsets[i+1]
            raw = data[start:end]
            
            try:
                text = raw.decode('cp949')
            except:
                text = repr(raw)
            out.write(f"{i:04d}: {text}\n")

dump_messages('/home/net77/koedit/scratch/gamedata/MESSAGE.DAT', '/home/net77/koedit/scratch/messages.txt')
