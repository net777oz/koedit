import zipfile, json, os

GAME_DATA_ZIP = '/home/net77/koedit/game_data/water2.zip'
MAPPING_FILE = '/home/net77/koedit/game_data/char_mapping.json'

def generate_mapping():
    try:
        with zipfile.ZipFile(GAME_DATA_ZIP, 'r') as z:
            data = z.read('KOUKAI2.DAT')
            
        mapping = []
        
        # 1. Sailors (Mates/Protags): 128 entries, 50 bytes each
        # We'll try to find the start by looking for "조안" again to be sure
        target = '조안'.encode('cp949')
        name_pos = data.find(target)
        if name_pos == -1: return "Error: Could not find Joan"
        
        # Assume entry starts 20 bytes before first name
        start_off = name_pos - 20
        
        for i in range(128):
            base = start_off + (i * 50)
            if base + 50 > len(data): break
            
            pid = data[base + 46] # Our best guess for Portrait ID
            first = data[base+20 : base+33].split(b'\x00')[0].decode('cp949', 'ignore').strip()
            last = data[base+33 : base+46].split(b'\x00')[0].decode('cp949', 'ignore').strip()
            
            mapping.append({
                "char_index": i,
                "type": "sailor",
                "offset": base,
                "size": 50,
                "portrait_id": pid,
                "name": f"{first} {last}".strip()
            })

        # 2. Barmaids/NPCs: 17 bytes entries starting at 0x1FAA
        npc_start = 0x1FAA
        for i in range(60):
            base = npc_start + (i * 17)
            if base + 17 > len(data): break
            name = data[base:base+11].split(b'\x00')[0].decode('cp949', 'ignore').strip()
            if not name: continue
            
            mapping.append({
                "char_index": i,
                "type": "npc",
                "offset": base,
                "size": 17,
                "portrait_id": 90 + i, # Placeholder or heuristic
                "name": name
            })

        with open(MAPPING_FILE, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, indent=2, ensure_ascii=False)
            
        return f"Successfully generated mapping for {len(mapping)} characters at {MAPPING_FILE}"
    except Exception as e:
        return f"Error: {str(e)}"

print(generate_mapping())
