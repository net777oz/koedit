import zipfile, json, os, re

GAME_DATA_ZIP = '/home/net77/koedit/game_data/water2.zip'
MAPPING_FILE = '/home/net77/koedit/game_data/char_mapping.json'

def clean_name(name):
    # Remove any non-printable or suspicious characters
    return re.sub(r'[^a-zA-Z0-9가-힣\s]', '', name).strip()

def generate_mapping():
    try:
        with zipfile.ZipFile(GAME_DATA_ZIP, 'r') as z:
            data = z.read('KOUKAI2.DAT')
            
        mapping = []
        # 1. Sailors (Mates): 128 entries, 50 bytes each, starts at 0x0695
        start_off = 0x0695
        for i in range(128):
            base = start_off + (i * 50)
            if base + 50 > len(data): break
            
            pid = data[base + 46]
            first = data[base+20 : base+33].split(b'\x00')[0].decode('cp949', 'ignore').strip()
            last = data[base+33 : base+46].split(b'\x00')[0].decode('cp949', 'ignore').strip()
            
            name = clean_name(f"{first} {last}")
            if not name: name = f"Mate {i}"
            
            mapping.append({
                "char_index": i,
                "type": "sailor",
                "offset": base,
                "size": 50,
                "portrait_id": pid,
                "name": name
            })

        # 2. Barmaids/NPCs: 17 bytes entries starting at 0x1FAD (Found by Matilda trace)
        npc_start = 0x1FAD
        # Usually there are portraits 1-128. Some NPCs use IDs > 100.
        # Let's map NPCs to higher IDs for now, but we need to be careful not to overwrite.
        for i in range(100):
            base = npc_start + (i * 17)
            if base + 17 > len(data): break
            name_chunk = data[base:base+11].split(b'\x00')[0]
            try:
                name = clean_name(name_chunk.decode('cp949', 'ignore'))
                if not name: continue
                
                # Heuristic: Find a likely portrait ID for these NPCs
                # Usually barmaids start from a certain ID in the portrait file
                # For now, let's keep them in the 129+ range to avoid collisions
                mapping.append({
                    "char_index": i,
                    "type": "npc",
                    "offset": base,
                    "size": 17,
                    "portrait_id": 128 + i, 
                    "name": name
                })
            except: pass

        with open(MAPPING_FILE, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, indent=2, ensure_ascii=False)
            
        return f"Successfully generated clean mapping for {len(mapping)} characters."
    except Exception as e:
        return f"Error: {str(e)}"

print(generate_mapping())
