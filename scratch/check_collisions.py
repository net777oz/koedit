import json

with open('/home/net77/koedit/game_data/char_mapping.json', 'r', encoding='utf-8') as f:
    mapping = json.load(f)

counts = {}
for e in mapping:
    pid = e['portrait_id']
    counts[pid] = counts.get(pid, []) + [e['name']]

print("Portrait ID Collisions (Multiple characters using same photo):")
for pid, names in sorted(counts.items()):
    if len(names) > 1:
        print(f"Portrait {pid+1:3}: {', '.join(names)}")

# Also check for specific characters the user mentioned
print("\nChecking specific characters:")
for e in mapping:
    if "조안" in e['name'] or "총독" in e['name'] or "피에트로" in e['name'] or "아론소" in e['name']:
        print(f"Name: {e['name']:15} | Portrait ID: {e['portrait_id']+1:3} | Offset: {e['offset']}")
