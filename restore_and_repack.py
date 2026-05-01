import shutil, os
for i in range(1, 129):
    fn = '{:04d}.png'.format(i)
    src = os.path.join('originals', fn)
    dst = os.path.join('export', fn)
    if os.path.exists(src):
        shutil.copy2(src, dst)
print('Restored all 128 originals to export/')

# Now repack and inject
import subprocess, zipfile
result = subprocess.run(['python3', 'koedit.py', 'pack'], capture_output=True, text=True)
print(result.stdout)
if result.returncode != 0:
    print('PACK FAILED:', result.stderr)
else:
    shutil.copy('KAO_NEW.LZW', 'KAO.LZW')
    for zp in ['web_client/game/water2.zip', 'web_client/static/game/water2.zip']:
        if os.path.exists(zp):
            tmp = zp + '.tmp'
            with zipfile.ZipFile(zp, 'r') as zin, zipfile.ZipFile(tmp, 'w') as zout:
                for item in zin.infolist():
                    if item.filename != 'KAO.LZW':
                        zout.writestr(item, zin.read(item.filename))
                zout.write('KAO.LZW', 'KAO.LZW')
            shutil.move(tmp, zp)
            print('Updated:', zp)
    print('All restored and repacked!')