import zipfile
import os
import shutil

zip_path = '/home/net77/koedit/web_client/game/water2.zip'
backup_path = '/home/net77/koedit/web_client/game/water2_backup.zip'

# 1. Restore SNR1.DAT from backup
with zipfile.ZipFile(backup_path, 'r') as z:
    original_snr1 = z.read('SNR1.DAT')

# 2. Apply safe replacement to the original data
old_seq = bytes([0xC0, 0x01, 0xCC, 0x00, 0x06, 0xC8, 0x00, 0x00])
new_seq = bytes([0xC0, 0x01, 0xCC, 0x00, 0x1F, 0xC8, 0x04, 0x94])

pos = original_snr1.find(old_seq)
if pos != -1:
    data = bytearray(original_snr1)
    data[pos:pos+len(new_seq)] = new_seq
    print(f"Replaced at 0x{pos:04X}")
    
    # Update zip
    temp_zip = zip_path + ".tmp"
    with zipfile.ZipFile(zip_path, 'r') as zin:
        with zipfile.ZipFile(temp_zip, 'w') as zout:
            for item in zin.infolist():
                if item.filename == 'SNR1.DAT':
                    zout.writestr('SNR1.DAT', data)
                    print("Updated SNR1.DAT")
                else:
                    zout.writestr(item, zin.read(item.filename))
    os.replace(temp_zip, zip_path)
    print("Clean safe patch applied!")
else:
    print("Original sequence not found in backup??")
