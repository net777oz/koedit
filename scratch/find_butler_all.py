import zipfile

backup_path = '/home/net77/koedit/web_client/game/water2_backup.zip'
with zipfile.ZipFile(backup_path, 'r') as z:
    data = z.read('SNR1.DAT')

# Search for C0 01 CC 00 06 C8 00 00
seq = bytes([0xC0, 0x01, 0xCC, 0x00, 0x06, 0xC8, 0x00, 0x00])

offsets = []
start = 0
while True:
    pos = data.find(seq, start)
    if pos == -1: break
    offsets.append(pos)
    start = pos + 1

print(f"Found {len(offsets)} occurrences of butler dialogue:")
for o in offsets:
    print(f"- 0x{o:04X}")
