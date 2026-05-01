import zipfile, os

src_zip = '/home/net77/koedit/backup_stable_v1/water2.zip'
dst_zip = '/home/net77/koedit/game_data/water2.zip'
target_file = 'SNR2.DAT'

# Extract from source
with zipfile.ZipFile(src_zip, 'r') as zin:
    data = zin.read(target_file)

# We can't easily 'replace' in zip with zipfile 'a' mode (it appends).
# Best to rebuild the zip or at least write it to a temp file and replace.
temp_zip = dst_zip + '.restore.tmp'
with zipfile.ZipFile(dst_zip, 'r') as zin, zipfile.ZipFile(temp_zip, 'w') as zout:
    for item in zin.infolist():
        if item.filename == target_file:
            zout.writestr(target_file, data)
        else:
            zout.writestr(item, zin.read(item.filename))

os.replace(temp_zip, dst_zip)
print(f"Successfully restored {target_file} from backup.")
