import struct

def read_messages(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    
    # Read first offset to know how many offsets there are
    first_offset = struct.unpack('>H', data[0:2])[0]
    num_messages = first_offset // 2
    
    offsets = []
    for i in range(num_messages):
        offset = struct.unpack('>H', data[i*2:i*2+2])[0]
        offsets.append(offset)
    offsets.append(len(data)) # End of file
    
    for i in range(5):
        start = offsets[i]
        end = offsets[i+1]
        raw = data[start:end]
        
        # Uncharted Waters 2 Korean version usually uses Johab (cp1361) or EUC-KR (cp949)
        try:
            text = raw.decode('cp949')
            enc = 'cp949'
        except:
            try:
                text = raw.decode('cp1361')
                enc = 'cp1361'
            except:
                text = repr(raw)
                enc = 'raw'
                
        print(f"Msg {i} ({enc}): {text}")

read_messages('/home/net77/koedit/scratch/gamedata/MESSAGE.DAT')
