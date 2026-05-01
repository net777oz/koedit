import zipfile
import os

zip_path = '/home/net77/koedit/game_data/water2.zip'
dest_path = '/home/net77/koedit/game_data/'

with zipfile.ZipFile(zip_path, 'r') as z:
    z.extract('SNR2.MES', dest_path)
    print("Extracted SNR2.MES to " + dest_path)
