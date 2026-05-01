import sys

def lzw_decode(data):
    # initialize dictionary
    dictionary = {i: bytes([i]) for i in range(256)}
    # wait, 256 and 257 might be special
    dict_size = 256
    bit_length = 9
    
    class BitStream:
        def __init__(self, data):
            self.data = data
            self.byte_idx = 0
            self.bit_idx = 0

        def read_bits(self, n):
            if self.byte_idx >= len(self.data): return None
            val = 0
            bits_read = 0
            while bits_read < n:
                if self.byte_idx >= len(self.data): break
                bits_available = 8 - self.bit_idx
                bits_to_read = min(n - bits_read, bits_available)
                
                # Big-endian or little-endian? Usually, LZW starts at LSB or MSB.
                # Assuming MSB first
                mask = (1 << bits_to_read) - 1
                shift = bits_available - bits_to_read
                chunk = (self.data[self.byte_idx] >> shift) & mask
                
                val = (val << bits_to_read) | chunk
                
                self.bit_idx += bits_to_read
                if self.bit_idx == 8:
                    self.bit_idx = 0
                    self.byte_idx += 1
                bits_read += bits_to_read
            return val

    bs = BitStream(data)
    out = bytearray()
    
    # Read first code
    old_code = bs.read_bits(bit_length)
    if old_code is None: return out
    out.extend(dictionary[old_code])
    
    while True:
        code = bs.read_bits(bit_length)
        if code is None: break
        
        if dict_size == 512: bit_length = 10
        elif dict_size == 1024: bit_length = 11
        elif dict_size == 2048: bit_length = 12
        elif dict_size == 4096: pass # dictionary full?
            
        if code in dictionary:
            entry = dictionary[code]
        elif code == dict_size:
            entry = dictionary[old_code] + bytes([dictionary[old_code][0]])
        else:
            print(f"Error: Invalid code {code} dict_size {dict_size}")
            break
            
        out.extend(entry)
        
        if dict_size < 4096:
            dictionary[dict_size] = dictionary[old_code] + bytes([entry[0]])
            dict_size += 1
            
        old_code = code

    return out

if __name__ == '__main__':
    with open('KAO.LZW', 'rb') as f:
        data = f.read()
    
    # Skip LS11 header?
    payload = data[16:]
    out = lzw_decode(payload)
    print("Decoded size (LS11 skipped):", len(out))
