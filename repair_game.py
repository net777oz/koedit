import os

path = '/home/net77/koedit/web_client/src/components/Game.tsx'
if os.path.exists(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove the dirty leftover snippets
    bad_snippets = [
        '};\n    frameId = requestAnimationFrame(loop);',
        '};\r\n    frameId = requestAnimationFrame(loop);',
        '    };\n    frameId = requestAnimationFrame(loop);',
        '    };\r\n    frameId = requestAnimationFrame(loop);'
    ]
    
    for bad in bad_snippets:
        content = content.replace(bad, '')
        
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Game.tsx repaired successfully.")
else:
    print("File not found.")
