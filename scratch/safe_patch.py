import zipfile
import os

zip_path = '/home/net77/koedit/web_client/game/water2.zip'

def safe_replace_event():
    with zipfile.ZipFile(zip_path, 'r') as z:
        data = bytearray(z.read('SNR1.DAT'))

    # Original sequence for Marco the butler
    # C0 01 CC 00 06 C8 00 00
    old_seq = bytes([0xC0, 0x01, 0xCC, 0x00, 0x06, 0xC8, 0x00, 0x00])
    # New sequence (Same size!)
    # C0 01 CC 00 1F C8 04 94
    new_seq = bytes([0xC0, 0x01, 0xCC, 0x00, 0x1F, 0xC8, 0x04, 0x94])

    pos = data.find(old_seq)
    if pos != -1:
        print(f"Found target sequence at 0x{pos:04X}. Replacing...")
        data[pos:pos+len(new_seq)] = new_seq
        
        # We don't need to update offsets because the size hasn't changed.
        
        # Save to a temporary file
        out_path = '/home/net77/koedit/scratch/gamedata/SNR1_SAFE.DAT'
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, 'wb') as f:
            f.write(data)
            
        print("Created SNR1_SAFE.DAT (Safe Replace)")
        return True
    else:
        print("Target sequence NOT found in SNR1.DAT. Maybe it was already modified?")
        return False

if safe_replace_event():
    # Update the zip
    temp_zip = zip_path + ".tmp"
    with zipfile.ZipFile(zip_path, 'r') as zin:
        with zipfile.ZipFile(temp_zip, 'w') as zout:
            for item in zin.infolist():
                if item.filename == 'SNR1.DAT':
                    zout.write('/home/net77/koedit/scratch/gamedata/SNR1_SAFE.DAT', 'SNR1.DAT')
                    print("Updated SNR1.DAT in zip.")
                else:
                    zout.writestr(item, zin.read(item.filename))
    os.replace(temp_zip, zip_path)
    print("Patch applied to water2.zip!")
