import sys

def ls11_decode(filename):
    with open(filename, 'rb') as f:
        data = f.read()

    if data[:4] != b'LS11':
        print("Not an LS11 file.")
        return

    dictionary = list(data[16:272])
    
    # LS11 typically uses a sliding window of some size. But some versions 
    # use a predefined 256-byte static dictionary for matches.
    # If the user mentioned "Koei-LZW", maybe it really IS LZW and the 256 bytes are the root strings?
    
    # Wait, another Koei LZ format uses exactly this: 256 byte dict + LZW bits. 
    # But let's try the common LS11 LZSS approach first.
    window = bytearray(4096)
    # How is window initialized? Sometimes with zeros, sometimes with the 256 dict repeated?
    # Or maybe the 256 dictionary is used as literal substitutions?
    
    # Actually, Koei LS11 decompresses as follows:
    # It reads a control byte. 
    # For each bit (MSB down to LSB):
    #   if 1: read literal, output it.
    #   if 0: read 2 bytes. offset, length. 
    
    src = 272
    out = bytearray()
    
    try:
        while src < len(data):
            # In LS11, there might not be a length defined, just EOF?
            flags = data[src]
            src += 1
            for i in range(8):
                if src >= len(data): break
                bit = (flags >> (7 - i)) & 1
                if bit == 1:
                    out.append(data[src])
                    src += 1
                else:
                    if src + 1 >= len(data): break
                    b1 = data[src]
                    b2 = data[src+1]
                    src += 2
                    
                    # Usually offset is 12 bits, length is 4 bits
                    # Let's say big endian: (b1 << 4) | (b2 >> 4) = offset
                    # Length: b2 & 0x0F
                    offset = ((b1 << 4) | (b2 >> 4))
                    length = (b2 & 0x0F) + 3 # or + something
                    
                    for _ in range(length):
                        # But wait, is it in the output buffer, or in the sliding window?
                        pass
                        
    except Exception as e:
        print(e)
        
    print(f"Decoded {len(out)} bytes roughly")

if __name__ == "__main__":
    ls11_decode(sys.argv[1])
