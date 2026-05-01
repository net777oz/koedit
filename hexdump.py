import sys

def hexdump(filename, size=256):
    try:
        with open(filename, 'rb') as f:
            data = f.read(size)
            print("Hex:", data.hex(' '))
            print("Ascii:", ''.join(chr(c) if 32 <= c < 127 else '.' for c in data))
            f.seek(0, 2)
            print("Total Size:", f.tell())
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    hexdump(sys.argv[1])
