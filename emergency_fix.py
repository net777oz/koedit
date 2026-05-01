import os

path = '/home/net77/koedit/web_client/src/components/Game.tsx'
if os.path.exists(path):
    with open(path, 'rb') as f:
        content = f.read().decode('utf-8', errors='ignore')

    # 깨진 한국어 문구 및 태그 수리
    replacements = {
        '<span>진행 ?이??초기??/span>': '<span>진행 데이터 초기화</span>',
        '<span>에뮬레이터 완??초기??(캐시 삭제)</span>': '<span>에뮬레이터 완전 초기화 (캐시 삭제)</span>',
        '<span>세이??파일 다운로드</span>': '<span>세이브 파일 다운로드</span>',
        '<span>세이??파일 가져오기</span>': '<span>세이브 파일 가져오기</span>',
        '<span>드롭박스에 세이??파일 저장하기</span>': '<span>드롭박스에 세이브 파일 저장하기</span>',
        '<span>드롭박스에서 세이??파일 가져오기</span>': '<span>드롭박스에서 세이브 파일 가져오기</span>'
    }

    for bad, good in replacements.items():
        content = content.replace(bad, good)
        
    # 혹시 모를 찌꺼기 중괄호 한 번 더 체크 (완벽 기함)
    if 'await fs.extract' in content:
        content = content.replace('};\n\n    const saveFileBody', '\n    const saveFileBody')

    with open(path, 'wb') as f:
        f.write(content.encode('utf-8'))
    print("Full Content Repair Successful")
else:
    print("File not found")
