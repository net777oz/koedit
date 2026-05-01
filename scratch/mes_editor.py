import struct
import sys
import os

def append_to_mes(in_file, out_file, new_text):
    with open(in_file, 'rb') as f:
        data = f.read()

    # SNR*.MES uses 32-bit big-endian offsets
    first_offset = struct.unpack('>I', data[0:4])[0]
    num_messages = first_offset // 4

    # Extract all original message chunks
    messages = []
    offsets = []
    for i in range(num_messages):
        offset = struct.unpack('>I', data[i*4:i*4+4])[0]
        offsets.append(offset)
    offsets.append(len(data))

    for i in range(num_messages):
        start = offsets[i]
        end = offsets[i+1]
        msg_data = data[start:end]
        # Ensure existing messages in our list end with 0x00 if we were to rebuild 
        # But here we just extract them as they are. 
        # (The original game messages ALREADY have 0x00 at the end)
        messages.append(msg_data)

    # Encode new text to CP949 and MUST add 0x00 terminator to prevent garbage characters
    new_data = new_text.encode('cp949') + b'\x00'
    messages.append(new_data)

    # Rebuild the file
    new_num_messages = len(messages)
    new_header_size = new_num_messages * 4
    
    out_header = bytearray()
    out_body = bytearray()
    
    current_offset = new_header_size
    for msg in messages:
        out_header.extend(struct.pack('>I', current_offset))
        out_body.extend(msg)
        current_offset += len(msg)
        
    with open(out_file, 'wb') as f:
        f.write(out_header)
        f.write(out_body)

    print(f"Success! Appended 1 new message with NULL terminator.")
    print(f"New total messages: {new_num_messages}")

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: python3 mes_editor.py <input.MES> <output.MES> \"<new text>\"")
        sys.exit(1)
    append_to_mes(sys.argv[1], sys.argv[2], sys.argv[3])
