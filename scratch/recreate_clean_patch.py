import zipfile
import struct
import os
import shutil

BASE_DIR = '/home/net77/koedit'
ZIP_BACKUP = os.path.join(BASE_DIR, 'web_client/game/water2_backup.zip')
SCRATCH_DIR = os.path.join(BASE_DIR, 'scratch/gamedata')
os.makedirs(SCRATCH_DIR, exist_ok=True)

# 1. Restore Original Files
with zipfile.ZipFile(ZIP_BACKUP, 'r') as z:
    orig_mes = z.read('SNR1.MES')
    orig_dat = z.read('SNR1.DAT')

# 2. Re-create CLEAN SNR1.MES (Add 0x00)
# (Using logic from mes_editor.py)
first_offset = struct.unpack('>I', orig_mes[0:4])[0]
num_messages = first_offset // 4
messages = []
offsets = [struct.unpack('>I', orig_mes[i*4:i*4+4])[0] for i in range(num_messages)]
offsets.append(len(orig_mes))

for i in range(num_messages):
    messages.append(orig_mes[offsets[i]:offsets[i+1]])

# Add new custom message with NULL terminator
new_msg = "§새로운 인물§ 안녕 조안! 내가 만든 새로운 이벤트 대사란다!".encode('cp949') + b'\x00'
messages.append(new_msg)

new_num = len(messages)
header_size = new_num * 4
new_mes_data = bytearray()
body_data = bytearray()
curr_off = header_size
for m in messages:
    new_mes_data.extend(struct.pack('>I', curr_off))
    body_data.extend(m)
    curr_off += len(m)
new_mes_data.extend(body_data)

with open(os.path.join(SCRATCH_DIR, 'SNR1_CLEAN.MES'), 'wb') as f:
    f.write(new_mes_data)

# 3. Re-apply Safe Patch to SNR1.DAT
old_seq = bytes([0xC0, 0x01, 0xCC, 0x00, 0x06, 0xC8, 0x00, 0x00])
new_seq = bytes([0xC0, 0x01, 0xCC, 0x00, 0x1F, 0xC8, 0x04, 0x94]) # 1172 = 0x0494

pos = orig_dat.find(old_seq)
new_dat_data = bytearray(orig_dat)
if pos != -1:
    new_dat_data[pos:pos+len(new_seq)] = new_seq
    print(f"Patched SNR1.DAT at 0x{pos:04X}")

with open(os.path.join(SCRATCH_DIR, 'SNR1_CLEAN.DAT'), 'wb') as f:
    f.write(new_dat_data)

print("Created Clean Patched Files in scratch/gamedata")
