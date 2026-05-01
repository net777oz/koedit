import os
import re

path = '/home/net77/koedit/web_client/src/components/Game.tsx'
if os.path.exists(path):
    with open(path, 'rb') as f:
        content = f.read().decode('utf-8', errors='ignore')

    # 1. Update HD Layer for better aspect ratio sync and debug visibility
    # We add border: "2px dashed #00ff00" to the debug mode to see the scanner area.
    overlay_fix = '''
          <div className="game__overlay-layer pointer-events-none absolute inset-0 overflow-hidden" style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%", pointerEvents: "none", zIndex: 100 }}>
            {detectedPortraits.map((p, idx) => (
              <div
                key={`layer-${p.id}-${idx}`}
                className="absolute"
                style={{
                  left: `${(p.x / 320) * 100}%`,
                  top: `${(p.y / 200) * 100}%`,
                  width: `${(64 / 320) * 100}%`,
                  height: `${(80 / 200) * 100}%`,
                  outline: "1px dashed rgba(0, 255, 0, 0.5)", // Scanner area indicator
                }}
              >
                <img
                  src={`http://localhost:5000/export/${String(p.id).padStart(4, "0")}.png`}
                  style={{
                    width: "100%",
                    height: "100%",
                    objectFit: "fill", // Match the game's stretch
                    imageRendering: "auto",
                  }}
                  onError={(e) => (e.currentTarget.style.display = "none")}
                />
              </div>
            ))}
          </div>
'''
    # Replace the existing layer with this improved version
    pattern = r'<div className="game__overlay-layer.*?</div>\s+</div>'
    content = re.sub(pattern, overlay_fix + '\n          </div>', content, flags=re.DOTALL)

    with open(path, 'wb') as f:
        f.write(content.encode('utf-8'))
    print("Aspect and Debug UI Improved.")
else:
    print("File not found.")
