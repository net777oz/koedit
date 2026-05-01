import os
import re

path = '/home/net77/koedit/web_client/src/components/Game.tsx'
if os.path.exists(path):
    with open(path, 'rb') as f:
        content = f.read().decode('utf-8', errors='ignore')

    # 1. Fix Screen Size (Make it 100% width/height or larger)
    content = content.replace('const [width, setWidth] = useState(640);', 'const [width, setWidth] = useState(window.innerWidth);')
    content = content.replace('const [height, setHeight] = useState(480);', 'const [height, setHeight] = useState(window.innerHeight);')
    
    # 2. Add Debug UI for detection status
    if 'Detected Portraits Status' not in content:
        debug_jsx = '''
          {/* Recognition Debug Info */}
          <div className="absolute top-2 left-2 bg-black/60 text-white p-2 text-xs z-[100] rounded pointer-events-none">
             <b>Vision Status:</b> {detectedPortraits.length > 0 ? "Detected " + detectedPortraits.map(p => "#" + p.id).join(", ") : "Scanning..."}
          </div>
'''
        content = content.replace('<div class="game">', '<div class="game">\n' + debug_jsx)

    # 3. Add responsive resize handler if it was missing
    if 'window.addEventListener("resize"' not in content:
        resize_code = '''
  useEffect(() => {
    const handleResize = () => {
      setWidth(window.innerWidth);
      setHeight(window.innerHeight);
    };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);
'''
        content = content.replace('useEffect(() => {\n    start();\n  }, [start]);', 
                                  'useEffect(() => {\n    start();\n  }, [start]);' + resize_code)

    with open(path, 'wb') as f:
        f.write(content.encode('utf-8'))
    print("Debug and Size UI Injected successfully.")
else:
    print("File not found.")
