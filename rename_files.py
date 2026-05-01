import os

export_dir = '/mnt/c/Ubuntu-24.04/home/net77/koedit/export'
for i in range(127, -1, -1):
    old_name = f"{i:04d}.png"
    new_name = f"{i+1:04d}.png"
    old_path = os.path.join(export_dir, old_name)
    new_path = os.path.join(export_dir, new_name)
    if os.path.exists(old_path):
        os.rename(old_path, new_path)
        print(f"Renamed {old_name} -> {new_name}")
