import sys
with open(sys.argv[1], 'rb') as f:
    f.seek(16)
    print("Dict preview:", f.read(16).hex(' '))
    f.seek(272)
    print("Data preview:", f.read(32).hex(' '))
