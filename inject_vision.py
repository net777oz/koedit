import os

path = '/home/net77/koedit/web_client/src/components/Game.tsx'
if os.path.exists(path):
    with open(path, 'rb') as f:
        content = f.read().decode('utf-8', errors='ignore')

    # 1. Add imports
    if 'OverlayScanner' not in content:
        content = content.replace('import { VirtualKeyboard } from "./VirtualKeyboard.tsx";', 
                                  'import { VirtualKeyboard } from "./VirtualKeyboard.tsx";\nimport { OverlayScanner, DetectedPortrait } from "../dos/overlay-engine";')

    # 2. Add state and ref
    if 'detectedPortraits' not in content:
        content = content.replace('const [innerToastMessage, setInnerToastMessage] = useState("");',
                                  'const [innerToastMessage, setInnerToastMessage] = useState("");\n  const [detectedPortraits, setDetectedPortraits] = useState<DetectedPortrait[]>([]);\n  const scannerRef = useRef<OverlayScanner>(new OverlayScanner());')

    # 3. Add scanner loop
    if 'scannerRef.current.scan' not in content:
        loop_code = '''
    // Start scanner loop
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

    # 4. Add JSX overlay layer
    if 'game__overlay-layer' not in content:
        overlay_jsx = '''
          <div className="game__overlay-layer pointer-events-none absolute inset-0 overflow-hidden">
            {detectedPortraits.map((p, idx) => (
              <img
                key={`${p.id}-${idx}`}
                src={`/static/hd_portraits/${String(p.id).padStart(4, "0")}.png`}
                className="absolute"
                style={{
                  left: `${(p.x / 320) * 100}%`,
                  top: `${(p.y / 200) * 100}%`,
                  width: `${(64 / 320) * 100}%`,
                  height: `${(80 / 200) * 100}%`,
                  imageRendering: "auto",
                }}
                onError={(e) => (e.currentTarget.style.display = "none")}
              />
            ))}
          </div>
'''
        content = content.replace('<canvas ref={canvas} />', '<canvas ref={canvas} />' + overlay_jsx)

    with open(path, 'wb') as f:
        f.write(content.encode('utf-8'))
    print('Injection successful')
else:
    print('File not found')
