import os
import re

path = '/home/net77/koedit/web_client/src/components/Game.tsx'
if os.path.exists(path):
    with open(path, 'rb') as f:
        data = f.read()

    # Define the mapping of patterns to correct Korean labels
    # We use regex to match the broken span content
    fixes = [
        (br'<span>.*?초기.*?</span>', '<span>진행 데이터 초기화</span>'),
        (br'<span>에뮬레이터.*?</span>', '<span>에뮬레이터 완전 초기화 (캐시 삭제)</span>'),
        (br'<span>세이.*?파일 다운로드</span>', '<span>세이브 파일 다운로드</span>'),
        (br'<span>세이.*?파일 가져오기</span>', '<span>세이브 파일 가져오기</span>'),
        (br'<span>.*?파일 가.*?오.*?</span>', '<span>세이브 파일 가져오기</span>'),
        (br'<span>.*?드롭박스.*?저장하기</span>', '<span>드롭박스에 세이브 파일 저장하기</span>'),
        (br'<span>.*?드롭박스.*?가져오기</span>', '<span>드롭박스에서 세이브 파일 가져오기</span>')
    ]

    for pattern, replacement in fixes:
        data = re.sub(pattern, replacement.encode('utf-8'), data)

    # Global cleanup for any weird tags
    data = data.replace(b'/span>', b'</span>')
    data = data.replace(b'</span></span>', b'</span>')
    
    # Fix the dangling brace if it still exists
    data = data.replace(b'    };\n    const saveFileBody', b'\n    const saveFileBody')
    data = data.replace(b'    };\r\n    const saveFileBody', b'\n    const saveFileBody')

    with open(path, 'wb') as f:
        f.write(data)
    print("Ultimate Fix Successful.")
else:
    print("File not found.")
