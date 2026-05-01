import os
import shutil
import subprocess
import zipfile
import json
import struct

CHAR_NAMES = {
    0x00: "시스템", 0x01: "조안", 0x02: "카탈리나", 0x03: "오토", 0x04: "에르네스트", 0x05: "피에트로", 0x06: "알리",
    0x07: "엔리코", 0x08: "필리", 0x09: "사누드", 0x0A: "에제키엘", 0x0B: "프랑코", 0x0C: "샤를롯", 0x0D: "루치아",
    0x0E: "안젤로", 0x0F: "조반니", 0x10: "마튜", 0x11: "앤드류", 0x12: "로코", 0x13: "한스", 0x14: "카를로",
    0x15: "니콜로", 0x16: "도메니코", 0x17: "안토니오", 0x18: "프란시스코", 0x19: "미구엘", 0x1A: "호세",
    0x1F: "로코(로또)", 0x20: "엔리코(조안부하)", 0x21: "필리(조안부하)", 0x22: "사누드(카탈부하)", 0x23: "에제키엘(카탈부하)",
    0x24: "레온 페레로", 0x25: "파브리스 페레로", 0x26: "카를로타", 0x27: "마르코", 0x28: "루크레치아", 0x29: "샤를롯",
    0x2D: "선원/부하", 0x31: "공관 관리인", 0x32: "항구 관리인", 0x33: "여관 주인", 0x34: "술집 주인",
    0x35: "교회 집사", 0x36: "도구점 주인", 0x37: "조선소 주인", 0x38: "주점 주인", 0x39: "조합 주인",
    0x3A: "은행원", 0x3B: "점성술사", 0x3C: "수집가", 0x3D: "주점 여급", 0x3E: "술집 여급", 
    0x3F: "노인", 0x40: "아이", 0x41: "사제", 0x42: "중동 상인", 0x43: "아프리카 상인", 0x44: "인도 상인",
    0x45: "동양 상인", 0x46: "원주민", 0x47: "해적", 0x48: "함대 사령관", 0x49: "국왕", 0x4A: "대신",
    0x64: "실비아", 0x65: "베아트리체", 0x66: "마르가리타", 0x67: "리사", 0x68: "루치아",
}

def get_message_map(snr_id):
    zip_path = '/home/net77/koedit/game_data/water2.zip'
    filename = f'SNR{snr_id}.MES'
    with zipfile.ZipFile(zip_path, 'r') as z:
        data = z.read(filename)
    
    messages = {}
    # Detect offset table: the first 4 bytes is an offset to the first message
    if len(data) < 4: return {}
    first_off = struct.unpack('>I', data[:4])[0]
    
    # Check if first_off looks like a valid offset (multiple of 4 and within file)
    if 0 < first_off < len(data) and first_off % 4 == 0:
        num_msgs = first_off // 4
        for i in range(num_msgs):
            off = struct.unpack('>I', data[i*4 : i*4+4])[0]
            if off >= len(data): break
            end = data.find(b'\x00', off)
            if end == -1: end = len(data)
            try:
                text = data[off:end].decode('cp949')
                messages[i] = text
            except:
                messages[i] = f"[Binary: {data[off:end].hex(' ')}]"
    else:
        # Fallback to split (for some versions)
        idx = 0
        msg_id = 0
        while idx < len(data):
            end = data.find(b'\x00', idx)
            if end == -1: break
            try:
                text = data[idx:end].decode('cp949')
                messages[msg_id] = text
            except:
                messages[msg_id] = f"[Binary: {data[idx:end].hex(' ')}]"
            msg_id += 1
            idx = end + 1
    return messages

def decompile_block_to_nodes(data, messages=None):
    nodes = {}
    labels = {0}
    # ... (rest of the logic remains similar but with text lookup)

OPCODE_LENGTHS = {
    0xC0: 2, 0xCC: 3, 0xC7: 1,
    0xAD: 4, 0xAC: 4, 0xAF: 4, 0xDC: 4,
    0x01: 1, 0x02: 1, 0x0F: 3, 0x8E: 5, 0x8F: 5,
    0xF1: 1, 0xF2: 1, 0xFE: 1, 0xCA: 5, 0xCB: 5,
    0xD4: 5, 0x0C: 3, 0xA0: 3, 0x8C: 3, 0x2C: 5,
    0x10: 5, 0x11: 5, 0xE9: 2, 0xF8: 1, 0x70: 3,
}

def decompile_block_to_nodes(data, messages=None):
    nodes = {}
    labels = {0} # Set of offsets that are targets of jumps
    
    # Detect the end of the initial offset table (marked by FFFFFFFF)
    code_start = 0
    table_end = data.find(b'\xFF\xFF\xFF\xFF')
    if table_end != -1:
        code_start = table_end + 4
        labels.add(code_start)
    
    # 1. First pass: Find all jump targets
    i = code_start
    while i < len(data):
        op = data[i]
        length = OPCODE_LENGTHS.get(op, 1)
        if op == 0xC8:
            if i + 1 < len(data):
                msg_len = data[i+1]
                if msg_len > 0 and i + 2 + msg_len < len(data) and data[i + 2 + msg_len] == 0x00:
                    length = 2 + msg_len + 1
                else:
                    length = 3
            else:
                length = 1
        
        if op in [0xAD, 0xAC, 0xAF, 0xDC] and i + 3 < len(data):
            addr = (data[i+2] << 8) | data[i+3]
            if addr < len(data):
                labels.add(addr)
        i += length
    
    # If code_start is > 0, we also want to see the table as node 0
    if code_start > 0:
        labels.add(0)

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
            
            # Special case for variable length dialogue
            if op == 0xC8:
                # Check if it looks like inlined text: C8 [LEN] [TEXT...] [00]
                is_inlined = False
                if curr + 1 < len(data):
                    msg_len = data[curr + 1]
                    # UW2 inlined text: the byte at (curr + 2 + msg_len) MUST be 0x00
                    if msg_len > 0 and curr + 2 + msg_len < len(data) and data[curr + 2 + msg_len] == 0x00:
                        is_inlined = True
                
                if is_inlined:
                    length = 2 + msg_len + 1
                else:
                    length = 3 # Fixed 3-byte ID reference
            
            cmd_bytes = data[curr:curr+length]
            
            human_info = ""
            is_significant = True
            
            if op == 0xC8:
                # If length > 3, it's definitely inlined
                if len(cmd_bytes) > 3:
                    try:
                        txt_bytes = cmd_bytes[2:]
                        if txt_bytes.endswith(b'\x00'): txt_bytes = txt_bytes[:-1]
                        human_info = f'💬 "{txt_bytes.decode("cp949")}"'
                    except:
                        human_info = f'💬 [인라인 데이터 오류]'
                else:
                    # 3-byte ID reference
                    msg_id = (cmd_bytes[1] << 8) | cmd_bytes[2]
                    human_info = f'💬 "{messages.get(msg_id, f"대사 {msg_id}")}"'
            elif op == 0xCC:
                char_id = cmd_bytes[2]
                human_info = f'👤 {CHAR_NAMES.get(char_id, f"인물 {char_id}")} 등장'
            elif op == 0xC0:
                pos = cmd_bytes[1]
                human_info = f'📍 위치: {"왼쪽" if pos == 1 else "오른쪽" if pos == 2 else "중앙"}'
            elif op == 0xAD:
                human_info = f'➔ [조건부 점프] {node_id}로 이동'
            elif op == 0xAC:
                human_info = f'🔍 [조건 체크] {node_id} 확인'
            elif op == 0xDC:
                human_info = f'🚀 [강제 이동] {node_id}로'
            elif op == 0xC7:
                is_significant = False # Wait for input is common, can be hidden
            else:
                # If it's a known small/junk opcode or single byte, mark as insignificant
                if length == 1 or op < 0x80:
                    is_significant = False
                else:
                    human_info = f'⚙️ 기타 동작 ({op:02X})'

            if op == 0xC8:
                is_inlined = (len(cmd_bytes) > 3)
                node_cmds.append({
                    "op": f"{op:02X}",
                    "bytes": cmd_bytes.hex(' '),
                    "offset": curr,
                    "text": human_info or f"코드 {op:02X}",
                    "significant": is_significant,
                    "is_inlined": is_inlined
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

def compile_nodes_to_block(nodes_dict):
    # Sort nodes by their original order (though we could reorder them)
    sorted_node_ids = sorted(nodes_dict.keys(), key=lambda x: int(x.split('_')[1], 16))
    
    # 1. First pass: Assign new offsets
    new_offsets = {}
    current_offset = 0
    for nid in sorted_node_ids:
        new_offsets[nid] = current_offset
        node = nodes_dict[nid]
        for cmd in node['commands']:
            current_offset += len(bytes.fromhex(cmd['bytes']))
            
    # 2. Second pass: Update jump targets and assemble bytes
    final_bytes = bytearray()
    for nid in sorted_node_ids:
        node = nodes_dict[nid]
        for cmd in node['commands']:
            raw = bytearray(bytes.fromhex(cmd['bytes']))
            op = raw[0]
            if op in [0xAD, 0xAC, 0xAF, 0xDC]:
                # Update the target address
                target_id = node['next_nodes'][0]
                if target_id in new_offsets:
                    new_addr = new_offsets[target_id]
                    raw[2] = (new_addr >> 8) & 0xFF
                    raw[3] = new_addr & 0xFF
            final_bytes.extend(raw)
            
    return bytes(final_bytes)
def compile_nodes_to_block(nodes_dict):
    # Pass 1: Calculate offsets for each node
    node_offsets = {}
    current_offset = 0
    # Sorting to maintain some consistency
    sorted_ids = sorted(nodes_dict.keys(), key=lambda x: (0 if '_' not in x else 1, x))
    
    for nid in sorted_ids:
        node_offsets[nid] = current_offset
        node = nodes_dict[nid]
        for cmd in node['commands']:
            op = int(cmd['op'], 16)
            if op == 0xC8:
                txt = cmd['text'].replace('💬 "', '').rstrip('"').encode('cp949', 'ignore')
                current_offset += 3 + len(txt) + 1
            elif op in [0xAD, 0xAC]: current_offset += 5
            elif op == 0xDC: current_offset += 3
            elif op in [0xC0, 0xCC]: current_offset += 3
            else:
                # Use original byte length from decompiler
                current_offset += len(bytes.fromhex(cmd['bytes']))
    
    # Pass 2: Generate bytes
    block_bytes = bytearray()
    for nid in sorted_ids:
        node = nodes_dict[nid]
        for cmd in node['commands']:
            op = int(cmd['op'], 16)
            block_bytes.append(op)
            if op == 0xC8:
                is_inlined = cmd.get('is_inlined', True)
                if is_inlined:
                    txt = cmd['text'].replace('💬 "', '').rstrip('"').encode('cp949', 'ignore')
                    block_bytes.append(len(txt) + 1)
                    block_bytes.extend(txt)
                    block_bytes.append(0x00)
                else:
                    # Keep original ID reference if text wasn't modified significantly
                    # (In a real case we might want to check if text matches MES, but for now
                    # we trust the is_inlined flag from decompiler)
                    orig = bytes.fromhex(cmd['bytes'])
                    block_bytes.extend(orig[1:])
            elif op in [0xAD, 0xAC]:
                target = node['next_nodes'][0] if node['next_nodes'] else nid
                off = node_offsets.get(target, 0)
                block_bytes.extend([0x00, 0x00]) # Params
                block_bytes.extend(struct.pack('<H', off)) # Internal offsets are Little Endian
            elif op == 0xDC:
                target = node['next_nodes'][0] if node['next_nodes'] else nid
                off = node_offsets.get(target, 0)
                block_bytes.extend(struct.pack('<H', off))
            elif op == 0xC0:
                block_bytes.extend([0x01, 0x01]) # Default pos
            elif op == 0xCC:
                block_bytes.extend([0x00, 0x02]) # Default Catalina
            else:
                orig = bytes.fromhex(cmd['bytes'])
                block_bytes.extend(orig[1:])
    return bytes(block_bytes)

def update_snr_with_nodes(snr_id, block_idx, nodes_dict):
    zip_path = '/home/net77/koedit/game_data/water2.zip'
    filename = f'SNR{snr_id}.DAT'
    
    with zipfile.ZipFile(zip_path, 'r') as z:
        data = bytearray(z.read(filename))
        
    # Compile new block data
    new_block_data = compile_nodes_to_block(nodes_dict)
    
    # Get current block info
    idx = 0x10 + (block_idx * 4)
    start = struct.unpack('>I', data[idx:idx+4])[0]
    next_val = struct.unpack('>I', data[idx+4:idx+8])[0]
    end = next_val if next_val != 0xFFFFFFFF else len(data)
    
    # Replace block data
    old_size = end - start
    new_size = len(new_block_data)
    diff = new_size - old_size
    
    new_data = data[:start] + new_block_data + data[end:]
    
    # Update all subsequent offsets in the header
    curr_idx = 0x10
    while True:
        off = struct.unpack('>I', new_data[curr_idx:curr_idx+4])[0]
        if off == 0xFFFFFFFF: break
        if off >= end:
            new_off = off + diff
            new_data[curr_idx:curr_idx+4] = struct.pack('>I', new_off)
        curr_idx += 4
        
    # Write back to zip
    temp_zip = zip_path + '.tmp'
    with zipfile.ZipFile(zip_path, 'r') as zin, zipfile.ZipFile(temp_zip, 'w') as zout:
        for it in zin.infolist():
            if it.filename == filename:
                zout.writestr(filename, new_data)
            else:
                zout.writestr(it, zin.read(it.filename))
    os.replace(temp_zip, zip_path)
    return True

def decompile_snr(filename, block_idx=0):
    zip_path = '/home/net77/koedit/game_data/water2.zip'
    snr_id = filename.replace('SNR', '').replace('.DAT', '')
    messages = get_message_map(snr_id)

    with zipfile.ZipFile(zip_path, 'r') as z:
        data = z.read(filename)
        
    idx = 0x10 + (block_idx * 4)
    start = struct.unpack('>I', data[idx:idx+4])[0]
    next_val = struct.unpack('>I', data[idx+4:idx+8])[0]
    end = next_val if next_val != 0xFFFFFFFF else len(data)
    
    block_data = data[start:end]
    return decompile_block_to_nodes(block_data, messages)

if __name__ == "__main__":
    result = decompile_snr('SNR2.DAT', 0)
    with open('/home/net77/koedit/scratch/snr2_nodes.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Decompiled {len(result)} nodes to scratch/snr2_nodes.json")
