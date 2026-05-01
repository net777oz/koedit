import struct
import zipfile

zip_path = '/home/net77/koedit/web_client/game/water2.zip'

def analyze_snr_commands(filename):
    with zipfile.ZipFile(zip_path, 'r') as z:
        data = z.read(filename)
    
    print(f"--- Analyzing {filename} ---")
    # Search for C8 [MsgID_High] [MsgID_Low]
    for i in range(len(data) - 2):
        if data[i] == 0xC8:
            msg_id = struct.unpack('>H', data[i+1:i+3])[0]
            # Print context (previous 5 bytes, next 5 bytes)
            context_pre = data[max(0, i-10):i].hex(' ')
            context_post = data[i+3:i+10].hex(' ')
            print(f"Offset 0x{i:04X}: MsgID {msg_id:4d} (0x{msg_id:04X}) | Pre: {context_pre} | Post: {context_post}")

analyze_snr_commands('SNR1.DAT')
