import sys

app_path = '/home/net77/koedit/app.py'
with open(app_path, 'r') as f:
    content = f.read()

patch = '''
GAME_DIST = os.path.join(BASE_DIR, 'web_client/dist')

@app.route('/emulator')
@app.route('/emulator/')
def serve_emulator():
    return send_from_directory(GAME_DIST, 'index.html')

@app.route('/emulator/<path:filename>')
def serve_emulator_assets(filename):
    return send_from_directory(GAME_DIST, filename)
'''

if 'GAME_DIST' not in content:
    content = content.replace('if __name__ == \'__main__\':', patch + '\nif __name__ == \'__main__\':')
    with open(app_path, 'w') as f:
        f.write(content)
    print('Patched app.py')
else:
    print('app.py already patched')
