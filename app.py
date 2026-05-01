import os, shutil, subprocess, zipfile, math
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect
from PIL import Image
import scenario_engine

app = Flask(__name__)
BASE_DIR = '/home/net77/koedit'
EXPORT_DIR = os.path.join(BASE_DIR, 'export')
VENV_PYTHON = os.path.join(BASE_DIR, 'venv/bin/python3')
GAME_DATA_DIR = os.path.join(BASE_DIR, 'game_data')
GAME_DATA_ZIP = os.path.join(GAME_DATA_DIR, 'water2.zip')
GAME_DIST = os.path.join(BASE_DIR, 'web_client/dist')

def create_breath_webp(input_path, output_path, frames=60, zoom_factor=0.08, pan_factor=0.03):
    try:
        img = Image.open(input_path).convert('RGBA')
        w, h = img.size; frame_list = []
        for i in range(frames):
            # Complex movement: Zoom + X-Pan + Y-Pan
            t = math.pi * 2 * i / frames
            zoom = 1.0 + (math.sin(t) + 1) / 2 * zoom_factor
            pan_x = math.sin(t * 0.5) * (w * pan_factor)
            pan_y = math.cos(t * 0.7) * (h * pan_factor * 0.5)
            
            new_w, new_h = int(w * zoom), int(h * zoom)
            resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            # Calculate crop with panning
            l = (new_w - w) / 2 + pan_x
            top = (new_h - h) / 2 + pan_y
            
            # Ensure crop stays within bounds
            l = max(0, min(l, new_w - w))
            top = max(0, min(top, new_h - h))
            
            frame_list.append(resized.crop((l, top, l + w, top + h)))
        
        frame_list[0].save(output_path, save_all=True, append_images=frame_list[1:], duration=40, loop=0, quality=90, method=6)
        return True
    except Exception as e: return False

@app.route('/')
def home(): return redirect('/editor')

@app.route('/editor')
@app.route('/editor/')
def index(): return render_template('index.html')

@app.route('/api/images')
def get_images():
    imgs = []
    names = {1: '조안 페레로', 2: '카탈리나 에란초', 3: '오토 스피노라', 4: '에르네스트 로페스', 5: '피에트로 콘티', 6: '알리 베자스'}
    for i in range(1, 129):
        p1_static = f'{i:04d}.png'
        p1_anim = f'{i:04d}_v1_anim.webp'
        p2_static = f'{i:04d}_v2_static.png'
        p2_anim = f'{i:04d}_v2_anim.webp'
        
        p = os.path.join(EXPORT_DIR, p1_static)
        if os.path.exists(p):
            img_info = {
                'id': i,
                'name': names.get(i, ''),
                'p1_static': f'/export/{p1_static}',
                'p1_anim': f'/export/{p1_anim}' if os.path.exists(os.path.join(EXPORT_DIR, p1_anim)) else None,
                'p2_static': f'/export/{p2_static}' if os.path.exists(os.path.join(EXPORT_DIR, p2_static)) else None,
                'p2_anim': f'/export/{p2_anim}' if os.path.exists(os.path.join(EXPORT_DIR, p2_anim)) else None
            }
            imgs.append(img_info)
    return jsonify({'images': imgs})

@app.route('/api/upload_v1/<int:image_id>', methods=['POST'])
def upload_v1(image_id):
    file = request.files.get('file')
    gen_gif = request.form.get('generate_gif') == 'true'
    if file:
        fn = f'{image_id:04d}.png'
        save_path = os.path.join(EXPORT_DIR, fn)
        file.save(save_path)
        if gen_gif:
            create_breath_webp(save_path, os.path.join(EXPORT_DIR, f'{image_id:04d}_v1_anim.webp'))
        return jsonify({'success': True})
    return jsonify({'error': 'no file'}), 400

@app.route('/api/upload_v2/<int:image_id>', methods=['POST'])
def upload_v2(image_id):
    file = request.files.get('file')
    gen_gif = request.form.get('generate_gif') == 'true'
    if file:
        fn = f'{image_id:04d}_v2_static.png'
        save_path = os.path.join(EXPORT_DIR, fn)
        file.save(save_path)
        if gen_gif:
            create_breath_webp(save_path, os.path.join(EXPORT_DIR, f'{image_id:04d}_v2_anim.webp'))
        return jsonify({'success': True})
    return jsonify({'error': 'no file'}), 400

@app.route('/api/upload_anim/<int:image_id>/<int:version>', methods=['POST'])
def upload_anim(image_id, version):
    file = request.files.get('file')
    if file:
        fn = f'{image_id:04d}_v{version}_anim.webp'
        file.save(os.path.join(EXPORT_DIR, fn))
        return jsonify({'success': True})
    return jsonify({'error': 'no file'}), 400

@app.route('/api/delete_anim/<int:image_id>/<int:version>', methods=['POST'])
def delete_anim(image_id, version):
    fn = f'{image_id:04d}_v{version}_anim.webp'
    p = os.path.join(EXPORT_DIR, fn)
    if os.path.exists(p): os.remove(p)
    return jsonify({'success': True})

@app.route('/api/delete_v2/<int:image_id>', methods=['POST'])
def delete_v2(image_id):
    for v in [f'{image_id:04d}_v2_static.png', f'{image_id:04d}_v2_anim.webp']:
        p = os.path.join(EXPORT_DIR, v)
        if os.path.exists(p): os.remove(p)
    return jsonify({'success': True})

@app.route('/api/reset/<int:image_id>', methods=['POST'])
def reset_image(image_id):
    # Reset P1 and its animation only
    fn = f'{image_id:04d}.png'
    src = os.path.join(BASE_DIR, 'originals', fn)
    if os.path.exists(src):
        shutil.copy(src, os.path.join(EXPORT_DIR, fn))
        v1_anim = os.path.join(EXPORT_DIR, f'{image_id:04d}_v1_anim.webp')
        if os.path.exists(v1_anim): os.remove(v1_anim)
        return jsonify({'success': True})
    return jsonify({'error': 'not found'}), 404

@app.route('/api/pack', methods=['POST'])
def pack_kao():
    subprocess.run([VENV_PYTHON, os.path.join(BASE_DIR, 'koedit.py'), 'pack'], cwd=BASE_DIR)
    new_kao = os.path.join(BASE_DIR, 'KAO_NEW.LZW')
    if os.path.exists(new_kao):
        tmp_zip = GAME_DATA_ZIP + '.tmp'
        with zipfile.ZipFile(GAME_DATA_ZIP, 'r') as zin:
            with zipfile.ZipFile(tmp_zip, 'w') as zout:
                for item in zin.infolist():
                    if item.filename == 'KAO.LZW': zout.write(new_kao, 'KAO.LZW')
                    else: zout.writestr(item, zin.read(item.filename))
        os.replace(tmp_zip, GAME_DATA_ZIP)
        return jsonify({'success': True, 'message': 'Packed and updated water2.zip!'})
    return jsonify({'error': 'KAO_NEW.LZW not found'}), 500

@app.route('/api/scenario/<int:snr_id>/<int:block_idx>')
def get_scenario(snr_id, block_idx):
    try: return jsonify(scenario_engine.decompile_snr(f'SNR{snr_id}.DAT', block_idx))
    except Exception as e: return jsonify({'error': str(e)}), 500

@app.route('/api/scenario/<int:snr_id>/<int:block_idx>', methods=['POST'])
def save_scenario(snr_id, block_idx):
    try:
        success = scenario_engine.update_snr_with_nodes(snr_id, block_idx, request.json); return jsonify({'success': success})
    except Exception as e: return jsonify({'error': str(e)}), 500

@app.route('/api/characters')
def get_characters(): return jsonify(scenario_engine.CHAR_NAMES)

@app.route('/export/<filename>')
def serve_export(filename): return send_from_directory(EXPORT_DIR, filename)

@app.route('/emulator')
@app.route('/emulator/')
def serve_emulator(): return send_from_directory(GAME_DIST, 'index.html')

@app.route('/emulator/<path:filename>')
@app.route('/static/game/<path:filename>')
def serve_assets(filename):
    if filename.endswith('water2.zip'): return send_from_directory(GAME_DATA_DIR, 'water2.zip')
    return send_from_directory(GAME_DIST, filename)

@app.route('/favicon-128x128.png')
def serve_favicon_png():
    path = os.path.join(GAME_DIST, 'favicon-128x128.png')
    if os.path.exists(path): return send_from_directory(GAME_DIST, 'favicon-128x128.png')
    return '', 204
@app.route('/favicon.ico')
def serve_favicon_ico():
    path = os.path.join(GAME_DIST, 'favicon.ico')
    if os.path.exists(path): return send_from_directory(GAME_DIST, 'favicon.ico')
    return '', 204

if __name__ == '__main__': app.run(host='0.0.0.0', port=5005)
