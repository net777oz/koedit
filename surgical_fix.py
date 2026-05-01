import os

path = '/home/net77/koedit/web_client/src/components/Game.tsx'
if os.path.exists(path):
    with open(path, 'rb') as f:
        content = f.read().decode('utf-8', errors='ignore')

    # Each button has a unique SVG path or icon. 
    # We will replace the entire button block where corruption is found.
    
    # 1. Reset Game Progress button
    if 'M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183' in content:
        content = content.replace('<span>진행 ?이??초기??/span>', '<span>진행 데이터 초기화</span>')
        # Catch any other variations
        import re
        content = re.sub(r'<span>진행.*?초기.*?</span>', '<span>진행 데이터 초기화</span>', content)

    # 2. Reset Emulator button
    content = re.sub(r'<span>에뮬레이터.*?초기.*?</span>', '<span>에뮬레이터 완전 초기화 (캐시 삭제)</span>', content)
    
    # 3. Save file download
    content = re.sub(r'<span>세이.*?파일 다운로드</span>', '<span>세이브 파일 다운로드</span>', content)
    
    # 4. Save file upload/import
    # SVG path for this is "M3.75 9.776c.112-.017.227-.026.344-.026h15.812..."
    content = re.sub(r'<span>.*?파일 가.*?오.*?</span>', '<span>세이브 파일 가져오기</span>', content)
    
    # 5. Dropbox Save
    content = re.sub(r'<span>드롭박스에 세이.*?파일 저장하기</span>', '<span>드롭박스에 세이브 파일 저장하기</span>', content)
    
    # 6. Dropbox Load
    content = re.sub(r'<span>드롭박스에서 세이.*?파일 가져오기</span>', '<span>드롭박스에서 세이브 파일 가져오기</span>', content)

    # Global Tag Integrity Check
    content = content.replace('/span>', '</span>')
    content = content.replace('</span></span>', '</span>')
    
    # Final syntax clean
    if 'await fs.extract' in content:
         import re
         # Clean up the curly brace mess after extract if it exists
         content = re.sub(r'};\s+const saveFileBody', '\n    const saveFileBody', content)

    with open(path, 'wb') as f:
        f.write(content.encode('utf-8'))
    print("Surgical Repair Successful.")
else:
    print("File not found.")
