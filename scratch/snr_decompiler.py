import struct
import zipfile
import json
import os

OPCODE_LENGTHS = {
    0xC0: 2, 0xCC: 3, 0xC8: 3, 0xC7: 1,
    0xAD: 4, 0xAC: 4, 0xAF: 4, 0xDC: 4,
    0x01: 1, 0x02: 1, 0x0F: 3, 0x8E: 5, 0x8F: 5,
    0xF1: 1, 0xF2: 1, 0xFE: 1, 0xCA: 5, 0xCB: 5,
    0xD4: 5, 0x0C: 3, 0xA0: 3, 0x8C: 3, 0x2C: 5,
    0x10: 5, 0x11: 5, 0xE9: 2, 0xF8: 1, 0x70: 3,
}

def decompile_block_to_nodes(data):
    nodes = {}
    labels = {0} # Set of offsets that are targets of jumps
    
    # 1. First pass: Find all jump targets to define node boundaries
    i = 0
    while i < len(data):
        op = data[i]
        length = OPCODE_LENGTHS.get(op, 1)
        if op in [0xAD, 0xAC, 0xAF, 0xDC]:
            addr = (data[i+2] << 8) | data[i+3]
            if addr < len(data):
                labels.add(addr)
        i += length

    # 2. Second pass: Group instructions into nodes
    sorted_labels = sorted(list(labels))
    for idx, start in enumerate(sorted_labels):
        end = sorted_labels[idx+1] if idx+1 < len(sorted_labels) else len(data)
        
        node_id = f"node_{start:04X}"
        node_cmds = []
        
        curr = start
        while curr < end:
            op = data[curr]
            length = OPCODE_LENGTHS.get(op, 1)
            cmd_bytes = data[curr:curr+length]
            
            node_cmds.append({
                "op": f"{op:02X}",
                "bytes": cmd_bytes.hex(' '),
                "offset": curr
            })
            
            # If this is a jump, record the exit target
            exit_target = None
            if op in [0xAD, 0xAC, 0xAF, 0xDC]:
                exit_target = f"node_{(data[curr+2] << 8) | data[curr+3]:04X}"
            
            curr += length
            
        nodes[node_id] = {
            "id": node_id,
            "offset": start,
            "commands": node_cmds,
            "next_nodes": [exit_target] if exit_target else ([f"node_{end:04X}"] if end < len(data) else [])
        }
        
    return nodes

def decompile_snr(filename, block_idx=0):
    zip_path = '/home/net77/koedit/game_data/water2.zip'
    with zipfile.ZipFile(zip_path, 'r') as z:
        data = z.read(filename)
        
    idx = 0x10 + (block_idx * 4)
    start = struct.unpack('>I', data[idx:idx+4])[0]
    next_val = struct.unpack('>I', data[idx+4:idx+8])[0]
    end = next_val if next_val != 0xFFFFFFFF else len(data)
    
    block_data = data[start:end]
    return decompile_block_to_nodes(block_data)

if __name__ == "__main__":
    result = decompile_snr('SNR1.DAT', 0)
    # Save a sample to scratch for inspection
    with open('/home/net77/koedit/scratch/snr1_nodes.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Decompiled {len(result)} nodes to scratch/snr1_nodes.json")
