import os, shutil, subprocess, zipfile, math, json
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

import sys

def get_in_game_names():
    mapping_path = os.path.join(BASE_DIR, 'game_data', 'char_mapping.json')
    if not os.path.exists(mapping_path):
        sys.stderr.write(f"Error: Mapping file not found at {mapping_path}\n")
        return {}
    try:
        with open(mapping_path, 'r', encoding='utf-8') as f:
            mapping = json.load(f)
        with zipfile.ZipFile(GAME_DATA_ZIP, 'r') as z:
            data = z.read('KOUKAI2.DAT')
        
        names = {}
        count = 0
        for entry in mapping:
            try:
                base = entry['offset']
                size = entry['size']
                pid = entry['portrait_id']
                
                # We skip if this portrait already has a name (prioritize first occurrences)
                if (pid + 1) in names:
                    continue

                if size == 50:
                    first = data[base+20 : base+33].split(b'\x00')[0]
                    last = data[base+33 : base+46].split(b'\x00')[0]
                    try: 
                        fname = first.decode('cp949', 'ignore').strip()
                        lname = last.decode('cp949', 'ignore').strip()
                        name = f"{fname} {lname}".strip()
                    except: name = entry.get('name', f"Char {pid}")
                else:
                    name_chunk = data[base : base+11].split(b'\x00')[0]
                    try: name = name_chunk.decode('cp949', 'ignore').strip()
                    except: name = entry.get('name', f"NPC {pid}")
                
                if name:
                    names[pid + 1] = name
                    count += 1
            except Exception as e:
                sys.stderr.write(f"Error processing entry: {e}\n")
                continue
        sys.stderr.write(f"Successfully loaded {count} unique portrait names.\n")
        return names
    except Exception as e:
        sys.stderr.write(f"Global error in get_in_game_names: {e}\n")
        return {}

@app.route('/api/images')
def get_images():
    imgs = []
    game_names = get_in_game_names()
    for i in range(1, 129):
        p1_static = f'{i:04d}.png'
        p1_anim = f'{i:04d}_v1_anim.webp'
        p2_static = f'{i:04d}_v2_static.png'
        p2_anim = f'{i:04d}_v2_anim.webp'
        p1_src = f'/export/{p1_static}'
        if not os.path.exists(os.path.join(EXPORT_DIR, p1_static)):
            if os.path.exists(os.path.join(BASE_DIR, 'originals', p1_static)):
                p1_src = f'/originals/{p1_static}'
            else: continue
        img_info = {
            'id': i,
            'name': game_names.get(i, f"Portrait {i}"),
            'p1_static': p1_src,
            'p1_anim': f'/export/{p1_anim}' if os.path.exists(os.path.join(EXPORT_DIR, p1_anim)) else None,
            'p2_static': f'/export/{p2_static}' if os.path.exists(os.path.join(EXPORT_DIR, p2_static)) else None,
            'p2_anim': f'/export/{p2_anim}' if os.path.exists(os.path.join(EXPORT_DIR, p2_anim)) else None
        }
        imgs.append(img_info)
    return jsonify({'images': imgs})

@app.route('/api/update_name/<int:image_id>', methods=['POST'])
def update_name(image_id):
    full_name = request.json.get('name', '')
    if not full_name: return jsonify({'error': 'empty name'}), 400
    
    mapping_path = os.path.join(BASE_DIR, 'game_data', 'char_mapping.json')
    try:
        with open(mapping_path, 'r', encoding='utf-8') as f:
            mapping = json.load(f)
        with zipfile.ZipFile(GAME_DATA_ZIP, 'r') as z:
            data = bytearray(z.read('KOUKAI2.DAT'))
        
        target_pid = image_id - 1
        updated = False
        for entry in mapping:
            if entry['portrait_id'] == target_pid:
                base = entry['offset']
                if entry['size'] == 50:
                    parts = full_name.split(' ', 1)
                    fname = parts[0]
                    lname = parts[1] if len(parts) > 1 else ""
                    f_enc = fname.encode('cp949', 'ignore')[:12]
                    data[base+20 : base+33] = f_enc.ljust(13, b'\x00')
                    l_enc = lname.encode('cp949', 'ignore')[:12]
                    data[base+33 : base+46] = l_enc.ljust(13, b'\x00')
                else: # NPC 17 bytes
                    encoded = full_name.encode('cp949', 'ignore')[:10]
                    data[base : base+11] = encoded.ljust(11, b'\x00')
                updated = True
        
        if not updated:
            return jsonify({'error': 'no character found for this portrait'}), 404
            
        tmp_zip = GAME_DATA_ZIP + '.tmp'
        with zipfile.ZipFile(GAME_DATA_ZIP, 'r') as zin, zipfile.ZipFile(tmp_zip, 'w') as zout:
            for item in zin.infolist():
                if item.filename == 'KOUKAI2.DAT': zout.writestr('KOUKAI2.DAT', data)
                else: zout.writestr(item, zin.read(item.filename))
        os.replace(tmp_zip, GAME_DATA_ZIP)
        return jsonify({'success': True})
    except Exception as e: return jsonify({'error': str(e)}), 500

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

@app.route('/originals/<filename>')
def serve_originals(filename): return send_from_directory(os.path.join(BASE_DIR, 'originals'), filename)

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
