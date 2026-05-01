import os

path = '/home/net77/koedit/web_client/src/components/Game.tsx'
if os.path.exists(path):
    with open(path, 'rb') as f:
        lines = f.readlines()

    final_lines = []
    for i, line in enumerate(lines):
        # frameId 할당 바로 뒤에 있는 '};'를 제거하여 구문 완성
        if b'};' in line and i > 0 and b'frameId = requestAnimationFrame(loop);' in lines[i-1]:
            print(f"Removed error line {i+1}")
            continue
        final_lines.append(line)

    with open(path, 'wb') as f:
        f.writelines(final_lines)
    print("Repair finished successfully.")
else:
    print("File not found.")
