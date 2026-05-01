import os
path = '/home/net77/koedit/web_client/src/components/Game.tsx'
with open(path, 'rb') as f:
    data = f.read()

# 패턴을 더 유연하게 검색하여 삭제
data = data.replace(b'};', b'', 1) # fs.extract 바로 뒤에 남은 것 하나만 삭제
data = data.replace(b'frameId = requestAnimationFrame(loop);', b'')

with open(path, 'wb') as f:
    f.write(data)
print('Fixed!')
