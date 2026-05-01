import os
import re

path = '/home/net77/koedit/web_client/src/components/Game.tsx'
if os.path.exists(path):
    with open(path, 'rb') as f:
        content = f.read().decode('utf-8', errors='ignore')

    # Define the entire correct Header Fns block (Korean labels fixed)
    correct_header_fns = '''
        <div
          class={`game__header__fns ${enabledToggleFns ? "game__header__fns--toggled" : ""}`}
        >
          <button
            type="button"
            class="game__header__fns__item"
            onClick={() => resetGame()}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
              className="size-6"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99"
              />
            </svg>
            <span>진행 데이터 초기화</span>
          </button>
          <button
            type="button"
            class="game__header__fns__item"
            onClick={() => resetGame(true)}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
              className="size-6"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0"
              />
            </svg>
            <span>에뮬레이터 완전 초기화 (캐시 삭제)</span>
          </button>
          <button
            type="button"
            class="game__header__fns__item"
            onClick={downloadSaveFile}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
              className="size-6"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3"
              />
            </svg>
            <span>세이브 파일 다운로드</span>
          </button>

          <button
            type="button"
            class="game__header__fns__item"
            onClick={uploadSaveFile}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
              className="size-6"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M3.75 9.776c.112-.017.227-.026.344-.026h15.812c.117 0 .232.009.344.026m-16.5 0a2.25 2.25 0 0 0-1.883 2.542l.857 6a2.25 2.25 0 0 0 2.227 1.932H19.05a2.25 2.25 0 0 0 2.227-1.932l.857-6a2.25 2.25 0 0 0-1.883-2.542m-16.5 0V6A2.25 2.25 0 0 1 6 3.75h3.879a1.5 1.5 0 0 1 1.06.44l2.122 2.12a1.5 1.5 0 0 0 1.06.44H18A2.25 2.25 0 0 1 20.25 9v.776"
              />
            </svg>
            <span>세이브 파일 가져오기</span>
          </button>
          <button
            type="button"
            class="game__header__fns__item"
            onClick={syncSaveFileToDropbox}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
              className="size-6"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M12 16.5V9.75m0 0 3 3m-3-3-3 3M6.75 19.5a4.5 4.5 0 0 1-1.41-8.775 5.25 5.25 0 0 1 10.233-2.33 3 3 0 0 1 3.758 3.848A3.752 3.752 0 0 1 18 19.5H6.75Z"
              />
            </svg>
            <span>드롭박스에 세이브 파일 저장하기</span>
          </button>
          <button
            type="button"
            class="game__header__fns__item"
            onClick={syncSaveFileFromDropbox}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
              className="size-6"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M12 16.5V9.75m0 0 3 3m-3-3-3 3M6.75 19.5a4.5 4.5 0 0 1-1.41-8.775 5.25 5.25 0 0 1 10.233-2.33 3 3 0 0 1 3.758 3.848A3.752 3.752 0 0 1 18 19.5H6.75Z"
              />
            </svg>
            <span>드롭박스에서 세이브 파일 가져오기</span>
          </button>
        </div>'''

    # Find the start and end of the broken block and replace it
    # We use a broad regex to find the block starting with game__header__fns
    pattern = r'<div\s+class={`game__header__fns.*?</div>\s+</div>\s+</div>'
    
    # Replacing with correct block + the closing divs for game__screen and game
    new_content = re.sub(pattern, correct_header_fns + '\n        </div>\n      </div>', content, flags=re.DOTALL)

    # One last surgery for the 'start' function to be 1000% sure
    # Ensure it ends with await main(...) and some handlers
    if 'await fs.extract' in new_content:
        new_content = re.sub(r'await fs\.extract.*?const saveFileBody', 'await fs.extract(`/static/game/${gameFile}?v=${Date.now()}`);\n\n    const saveFileBody', new_content, flags=re.DOTALL)

    # Ensure no stray curly brace after frameId
    new_content = new_content.replace('    };\n    const saveFileBody', '\n    const saveFileBody')
    new_content = new_content.replace('    };\r\n    const saveFileBody', '\n    const saveFileBody')

    with open(path, 'wb') as f:
        f.write(new_content.encode('utf-8'))
    print("Mega Repair Successful.")
else:
    print("File not found.")
