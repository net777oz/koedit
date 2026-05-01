import struct
import zipfile

zip_path = '/home/net77/koedit/game_data/water2.zip'

def scan_jumps(filename):
    with zipfile.ZipFile(zip_path, 'r') as z:
        data = z.read(filename)
    
    print(f"--- Scanning {filename} for Potential Jumps ---")
    
    # We'll look for AD, AE, AF, AC opcodes
    # and try to see if the following bytes look like valid offsets (0x0000 - 0x3FFF)
    for i in range(len(data) - 4):
        op = data[i]
        if op in [0xAD, 0xAE, 0xAF, 0xAC]:
            val1 = data[i+1]
            val2 = data[i+2]
            val3 = data[i+3]
            
            # Potential 16-bit address (big endian)
            addr = (val2 << 8) | val3
            
            # If the address is within the data block range...
            if 0 < addr < len(data):
                context = data[i:i+8].hex(' ')
                print(f"Offset 0x{i:04X}: Op {op:02X} | Potential Addr: 0x{addr:04X} | Bytes: {context}")

scan_jumps('SNR1.DAT')
