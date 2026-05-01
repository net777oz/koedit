import os
import re

path = '/home/net77/koedit/web_client/src/components/Game.tsx'
if os.path.exists(path):
    with open(path, 'rb') as f:
        content = f.read().decode('utf-8', errors='ignore')

    # Ensure we don't have previous messy partial injections
    if 'OverlayScanner' in content:
        print("Cleaning up old injection traces...")
        # Simple cleanup if needed, but the current file should be the restored clean one.

    # 1. Add Imports
    if 'OverlayScanner' not in content:
        content = content.replace('import { VirtualKeyboard } from "./VirtualKeyboard.tsx";', 
                                  'import { VirtualKeyboard } from "./VirtualKeyboard.tsx";\nimport { OverlayScanner, DetectedPortrait } from "../dos/overlay-engine";')

    # 2. Add State and Ref
    if 'detectedPortraits' not in content:
        state_code = '  const [detectedPortraits, setDetectedPortraits] = useState<DetectedPortrait[]>([]);\n  const scannerRef = useRef<OverlayScanner>(new OverlayScanner());'
        content = content.replace('const [enabledToggleFns, setEnabledToggleFns] = useState(false);', 
                                  'const [enabledToggleFns, setEnabledToggleFns] = useState(false);\n' + state_code)

    # 3. Add Scanner Loop
    if 'scannerRef.current.scan' not in content:
        loop_code = '''
    // Start HD Vision Loop
    let frameId: number;
    const loop = () => {
      if (canvas.current) {
        const found = scannerRef.current.scan(canvas.current);
        setDetectedPortraits((prev) => {
          if (JSON.stringify(prev) === JSON.stringify(found)) return prev;
          return found;
        });
      }
      frameId = requestAnimationFrame(loop);
    };
    frameId = requestAnimationFrame(loop);
'''
        content = content.replace('await fs.extract(`/static/game/${gameFile}?v=${Date.now()}`);',
                                  'await fs.extract(`/static/game/${gameFile}?v=${Date.now()}`);' + loop_code)

    # 4. Add HD Layer JSX
    if 'game__overlay-layer' not in content:
        overlay_jsx = '''
          <div className="game__overlay-layer pointer-events-none absolute inset-0 overflow-hidden" style={{ zIndex: 1, pointerEvents: 'none' }}>
            {detectedPortraits.map((p, idx) => (
              <img
                key={`hd-${p.id}-${idx}`}
                src={`http://localhost:5000/export/${String(p.id).padStart(4, "0")}.png`}
                className="absolute"
                style={{
                  left: `${(p.x / 320) * 100}%`,
                  top: `${(p.y / 200) * 100}%`,
                  width: `${(64 / 320) * 100}%`,
                  height: `${(80 / 200) * 100}%`,
                  imageRendering: "auto",
                  border: "none"
                }}
                onError={(e) => (e.currentTarget.style.display = "none")}
              />
            ))}
          </div>
'''
        content = content.replace('<canvas ref={canvas} />', '<canvas ref={canvas} />\n' + overlay_jsx)

    with open(path, 'wb') as f:
        f.write(content.encode('utf-8'))
    print("Injection successful.")
else:
    print("File not found.")
