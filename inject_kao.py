import shutil, zipfile, os

base = "/home/net77/koedit"
kao_new = os.path.join(base, "KAO_NEW.LZW")
kao_orig = os.path.join(base, "KAO.LZW")

shutil.copy(kao_new, kao_orig)
print("Copied KAO_NEW.LZW -> KAO.LZW")

targets = [
    os.path.join(base, "web_client/game/water2.zip"),
    os.path.join(base, "web_client/static/game/water2.zip"),
]

for zip_path in targets:
    if os.path.exists(zip_path):
        tmp_zip = zip_path + ".tmp"
        with zipfile.ZipFile(zip_path, "r") as zin, zipfile.ZipFile(tmp_zip, "w") as zout:
            for item in zin.infolist():
                if item.filename != "KAO.LZW":
                    zout.writestr(item, zin.read(item.filename))
            zout.write(kao_orig, "KAO.LZW")
        shutil.move(tmp_zip, zip_path)
        print("Updated: " + zip_path)
        with zipfile.ZipFile(zip_path, "r") as z:
            info = z.getinfo("KAO.LZW")
            print("  KAO.LZW in zip: {} bytes".format(info.file_size))
    else:
        print("NOT FOUND: " + zip_path)

print("All done!")