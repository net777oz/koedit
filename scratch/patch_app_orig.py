import os

app_path = '/home/net77/koedit/app.py'
with open(app_path, 'r') as f:
    content = f.read()

if '/originals/' not in content:
    patch = '''
@app.route('/originals/<filename>')
def serve_originals(filename): return send_from_directory(os.path.join(BASE_DIR, 'originals'), filename)
'''
    content = content.replace('def serve_export(filename): return send_from_directory(EXPORT_DIR, filename)', 'def serve_export(filename): return send_from_directory(EXPORT_DIR, filename)' + patch)
    
    with open(app_path, 'w') as f:
        f.write(content)
    print('Patched app.py with /originals/')
else:
    print('app.py already has /originals/')
