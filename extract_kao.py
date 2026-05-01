import zipfile
import os
import sys

def main():
    zip_path = sys.argv[1]
    extract_to = sys.argv[2]

    print(f"Extracting KAO.LZW from {zip_path} to {extract_to}")
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extract('KAO.LZW', extract_to)
        
    extracted_file = os.path.join(extract_to, 'KAO.LZW')
    print(f"Extraction successful! File size: {os.path.getsize(extracted_file)} bytes")

if __name__ == "__main__":
    main()
