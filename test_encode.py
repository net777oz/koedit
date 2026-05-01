import bitarray

def encode_code(code: int) -> bitarray.bitarray:
    N = code + 2
    binary_str = bin(N)[2:]  # e.g. code 0 -> N=2 -> '10' -> mask_len=1
    mask_len = len(binary_str) - 1
    
    a = bitarray.bitarray()
    # Unary part
    for _ in range(mask_len - 1):
        a.append(1)
    a.append(0)
    
    # Factor part
    for char in binary_str[1:]:
        a.append(int(char))
    return a

# Test get_codes parity
def test():
    import random
    codes = [random.randint(0, 500) for _ in range(100)]
    stream = bitarray.bitarray()
    for code in codes:
        stream.extend(encode_code(code))
    
    # add a bunch of 1s to simulate EOF or just stop where it shouldn't crash
    # get_codes loop relies on pos < pos_end.
    
    # Let's import get_codes from ls11
    import sys
    sys.path.append('kaodata/dekoei')
    from ls11 import get_codes
    
    data = stream.tobytes()
    decoded_codes = get_codes(data)
    
    # get_codes might over-read if the stream is padded with 0s at the end
    # but the first 100 codes should match precisely!
    print("Match?", codes == decoded_codes[:100])

if __name__ == '__main__':
    test()
