import os
import re

path = '/home/net77/koedit/web_client/src/components/Game.tsx'
if os.path.exists(path):
    with open(path, 'rb') as f:
        content = f.read().decode('utf-8', errors='ignore')

    # Remove scanner imports
    content = content.replace('import { OverlayScanner, DetectedPortrait } from "../dos/overlay-engine";', '')
    
    # Remove added states/refs
    content = content.replace('const [detectedPortraits, setDetectedPortraits] = useState<DetectedPortrait[]>([]);', '')
    content = content.replace('const scannerRef = useRef<OverlayScanner>(new OverlayScanner());', '')

    # Fix the useEffect logic (restore to simple fs.extract)
    # Using a more surgical replacement to avoid breaking other parts
    pattern = r'await fs\.extract\(`.*?`\);.*?const saveFileBody = await db\.load\(saveFile\);'
    replacement = 'await fs.extract(`/static/game/${gameFile}?v=${Date.now()}`);\n\n    const saveFileBody = await db.load(saveFile);'
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    # Remove Overlay Layer JSX
    content = re.sub(r'<div className="game__overlay-layer.*?</div>\s+</div>', '        </div>', content, flags=re.DOTALL)

    # Final cleanup of any broken span text or weird braces
    content = re.sub(r'<span>진행.*?초기.*?</span>', '<span>진행 데이터 초기화</span>', content)
    content = re.sub(r'<span>에뮬레이터.*?초기.*?</span>', '<span>에뮬레이터 완전 초기화 (캐시 삭제)</span>', content)
    content = re.sub(r'<span>세이.*?파일 다운로드</span>', '<span>세이브 파일 다운로드</span>', content)
    content = re.sub(r'<span>.*?파일 가.*?오.*?</span>', '<span>세이브 파일 가져오기</span>', content)
    content = re.sub(r'<span>드롭박스.*?저장하기</span>', '<span>드롭박스에 세이브 파일 저장하기</span>', content)
    content = re.sub(r'<span>드롭박스.*?가져오기</span>', '<span>드롭박스에서 세이브 파일 가져오기</span>', content)

    # Fix any potential double braces or stray closing tags
    content = content.replace('};\n\n    const saveFileBody', '\n    const saveFileBody')
    content = content.replace('};\r\n    const saveFileBody', '\n    const saveFileBody')

    with open(path, 'wb') as f:
        f.write(content.encode('utf-8'))
    print("Game.tsx Revert Successful")
else:
    print("File not found")
