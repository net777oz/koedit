import os
import re

path = '/home/net77/koedit/web_client/src/components/Game.tsx'
if os.path.exists(path):
    with open(path, 'rb') as f:
        content = f.read().decode('utf-8', errors='ignore')

    # 1. Ensure the canvas container is relative for absolute children (overlay)
    if '<div class="game__canvas">' in content:
        content = content.replace('<div class="game__canvas">', '<div class="game__canvas" style={{ position: "relative" }}>')
        
    # 2. Adjust Overlay Layer to fill the container perfectly
    if 'game__overlay-layer' in content:
        content = content.replace('className="game__overlay-layer pointer-events-none absolute inset-0 overflow-hidden"', 
                                  'className="game__overlay-layer pointer-events-none absolute inset-0 overflow-hidden" style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%", pointerEvents: "none", zIndex: 100 }}')

    with open(path, 'wb') as f:
        f.write(content.encode('utf-8'))
    print("Layout Alignment Fixed.")
else:
    print("File not found.")
