import zipfile

zip_path = '/home/net77/koedit/web_client/game/water2.zip'
with zipfile.ZipFile(zip_path, 'r') as z:
    data = z.read('EVENT1.DAT')

# Find all C8 commands
found = []
for i in range(len(data)-2):
    if data[i] == 0xC8:
        msg_id = (data[i+1] << 8) | data[i+2]
        found.append((i, msg_id))

print(f"EVENT1.DAT has {len(found)} C8 commands.")
for pos, mid in found[:20]:
    print(f"- Offset 0x{pos:04X}: MsgID {mid}")
