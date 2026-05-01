import struct
import zipfile

zip_path = '/home/net77/koedit/game_data/water2.zip'

def analyze_block_structure(filename):
    with zipfile.ZipFile(zip_path, 'r') as z:
        data = z.read(filename)
    
    # Extract header offsets
    offsets = []
    idx = 0x10
    while True:
        val = struct.unpack('>I', data[idx:idx+4])[0]
        if val == 0xFFFFFFFF: break
        offsets.append(val)
        idx += 4
    
    # Analyze Block 0
    start = offsets[0]
    end = offsets[1] if len(offsets) > 1 else len(data)
    block_data = data[start:end]
    
    print(f"Block 0: Start=0x{start:04X}, Size={len(block_data)}")
    
    # Find all potential 2-byte addresses following AD, AC, AF, DC
    # Big Endian
    for i in range(len(block_data) - 4):
        op = block_data[i]
        if op in [0xAD, 0xAC, 0xAF, 0xDC]:
            # For AD/AC/AF, usually it's OP XX YY ZZ (4 bytes)
            # For DC, let's see. 
            addr = (block_data[i+2] << 8) | block_data[i+3]
            
            # Check if this address points to another Opcode start
            # A good heuristic: Does it point to a known Opcode like C0, CC, C8, AD, AC?
            if addr < len(block_data):
                target_op = block_data[addr]
                if target_op in [0xC0, 0xCC, 0xC8, 0xAD, 0xAC, 0xC7, 0x01, 0x02]:
                    print(f"CONFIRMED JUMP: At Block+0x{i:04X} (Op {op:02X}) -> Target Block+0x{addr:04X} (Target Op {target_op:02X})")

analyze_block_structure('SNR1.DAT')
