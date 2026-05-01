import sys

def search_text(filename, keywords):
    with open(filename, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if any(k in line for k in keywords):
                print(f"[{i}]: {line.strip()}")

search_text('/home/net77/koedit/scratch/messages.txt', ['레온', '조안', '페레로', '엔리코', '마르코', '로코', '카탈리나'])
