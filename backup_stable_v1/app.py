import os, shutil, subprocess, zipfile, tempfile
from flask import Flask, render_template, request, jsonify, send_from_directory
app = Flask(__name__)
BASE_DIR = '/home/net77/koedit'
EXPORT_DIR = os.path.join(BASE_DIR, 'export')
VENV_PYTHON = os.path.join(BASE_DIR, 'venv/bin/python3')
@app.route('/')
def index(): return render_template('index.html')
@app.route('/api/images')
def get_images():
    names = {1: '조안 페레로', 2: '카탈리나 에란초', 3: '오토 스피노라', 4: '에르네스트 로페스', 5: '피에트로 콘티', 6: '알리 베자스'}
    imgs = []
    for i in range(1, 129):
        fn = f'{i:04d}.png'
        if os.path.exists(os.path.join(EXPORT_DIR, fn)):
            imgs.append({'id': i, 'url': f'/export/{fn}', 'name': names.get(i, '')})
    return jsonify({'images': imgs})
@app.route('/api/upload/<int:image_id>', methods=['POST'])
def upload_image(image_id):
    file = request.files.get('file')
    if file:
        file.save(os.path.join(EXPORT_DIR, f'{image_id:04d}.png'))
        return jsonify({'success': True})
    return jsonify({'error': 'no file'}), 400
@app.route('/api/reset/<int:image_id>', methods=['POST'])
def reset_image(image_id):
    fn = f'{image_id:04d}.png'; src = os.path.join(BASE_DIR, 'originals', fn)
    if os.path.exists(src):
        shutil.copy(src, os.path.join(EXPORT_DIR, fn))
        return jsonify({'success': True})
    return jsonify({'error': 'not found'}), 404
@app.route('/api/pack', methods=['POST'])
def pack_kao():
    subprocess.run([VENV_PYTHON, os.path.join(BASE_DIR, 'koedit.py'), 'pack'], cwd=BASE_DIR)
    kn, ko = os.path.join(BASE_DIR, 'KAO_NEW.LZW'), os.path.join(BASE_DIR, 'KAO.LZW')
    if os.path.exists(kn):
        shutil.copy(kn, ko); targets = [os.path.join(BASE_DIR, 'web_client/game/water2.zip'), os.path.join(BASE_DIR, 'web_client/static/game/water2.zip')]
        for zp in targets:
            if os.path.exists(zp):
                tz = zp + '.tmp'
                with zipfile.ZipFile(zp, 'r') as zin, zipfile.ZipFile(tz, 'w') as zout:
                    for it in zin.infolist():
                        if it.filename != 'KAO.LZW': zout.writestr(it, zin.read(it.filename))
                    zout.write(ko, 'KAO.LZW')
                shutil.move(tz, zp)
        return jsonify({'success': True})
    return jsonify({'error': 'fail'}), 500
@app.route('/export/<filename>')
def serve_export(filename): return send_from_directory(EXPORT_DIR, filename)
if __name__ == '__main__': app.run(host='0.0.0.0', port=5000, debug=True)
