import os

def encode_LZSS(data):
    i = 0
    tokens = []
    buffer_size = 1000
    while i < len(data):
        buffer = data[max(0, i - buffer_size):i]
        match_offset, match_length = -1, 0
        max_length = min(18, len(data) - i)
        for length in range(3, max_length + 1):
            sub = data[i:i + length]
            pos = buffer.find(sub)
            if pos != -1:
                match_offset = len(buffer) - pos
                match_length = length

        if match_length >= 3:
            tokens.append((1, (match_offset, match_length)))
            i += match_length
        else:
            tokens.append((0, data[i:i+1]))
            i += 1

    output = bytearray()
    j = 0
    while j < len(tokens):
        block_tokens = tokens[j:j+8]
        flag = 0
        block_data = bytearray()
        for bit, (flag_bit, token) in enumerate(block_tokens):
            flag = (flag << 1) | flag_bit
            if flag_bit:
                offset, length = token
                block_data.append(offset & 0xFF)
                block_data.append(length & 0xFF)
            else:
                block_data.append(token[0])
        shift_amount = 8 - len(block_tokens)
        flag = flag << shift_amount
        output.append(flag)
        output.extend(block_data)
        j += 8

    return bytes(output)


def decode_LZSS(encoded_data):
    output = bytearray()
    i = 0

    while i < len(encoded_data):
        flags = encoded_data[i]
        i += 1

        for bit in range(7, -1, -1):
            if i >= len(encoded_data):
                break

            if (flags >> bit) & 1:
                if i + 1 >= len(encoded_data):
                    break
                offset = encoded_data[i]
                length = encoded_data[i + 1]
                i += 2

                if offset == 0 or offset > len(output):
                    raise ValueError(f"Невозможное значение offset: {offset}")

                start = len(output) - offset
                for _ in range(length):
                    output.append(output[start])
                    start += 1
            else:  # Флаг == 0: литерал
                output.append(encoded_data[i])
                i += 1

    return bytes(output)

def lz77_encode(data: bytes, buffer_size: int) -> bytes:
    encoded_data = bytearray()
    i = 0
    n = len(data)

    while i < n:
        max_length = 0
        max_offset = 0
        search_start = max(0, i - buffer_size)
        search_end = i
        for length in range(min(255, n - i), 0, -1):
            substring = data[i:i + length]
            offset = data[search_start:search_end].rfind(substring)
            if offset != -1:
                max_length = length
                max_offset = search_end - search_start - offset
                break

        if max_length > 0:
            encoded_data.append((max_offset >> 8) & 0xFF)
            encoded_data.append(max_offset & 0xFF)
            encoded_data.append((max_length >> 8) & 0xFF)
            encoded_data.append(max_length & 0xFF)
            i += max_length
        else:
            encoded_data.append(0)
            encoded_data.append(0)
            encoded_data.append(0)
            encoded_data.append(0)
            encoded_data.append(data[i])
            i += 1

    return bytes(encoded_data)


def lz77_decode(encoded_data: bytes) -> bytes:
    decoded_data = bytearray()
    i = 0
    n = len(encoded_data)
    while i < n:
        offset = (encoded_data[i] << 8) | encoded_data[i + 1]
        length = (encoded_data[i + 2] << 8) | encoded_data[i + 3]
        i += 4
        if offset == 0 and length == 0:
            decoded_data.append(encoded_data[i])
            i += 1
        else:
            start = len(decoded_data) - offset
            end = start + length
            decoded_data.extend(decoded_data[start:end])
    return bytes(decoded_data)

def compr_text(input, compr, decompr):#4
    b=1024
    with open(input, "rb") as file_input, open(compr, "wb") as file_output:
        S = file_input.read()
        lz=lz77_encode(S, b)
        file_output.write(lz)
    orig_size=os.path.getsize(input)
    compr_size=os.path.getsize(compr)
    print("Размер до сжатия: "+str(orig_size))
    print("Размер после сжатия: "+str(compr_size))
    k=orig_size/compr_size
    with open(compr, "rb") as file_input, open(decompr, "w", encoding="utf-8") as file_output:
        Sc = file_input.read()
        S=lz77_decode(Sc)
        S = S.decode("utf-8")
        file_output.write(S)

    decompr_size = os.path.getsize(decompr)
    print("Размер после декомпрессии: " + str(decompr_size))
    return k

def compr_enwik(input, compr, decompr):#4
    b=1024
    with open(input, "rb") as file_input, open(compr, "wb") as file_output:
        S = file_input.read()
        lz = lz77_encode(S,b)
        file_output.write(lz)
    orig_size = os.path.getsize(input)
    compr_size = os.path.getsize(compr)
    print("Размер до сжатия: "+str(orig_size))
    print("Размер после сжатия: "+str(compr_size))
    k=orig_size/compr_size
    i=0
    with open(compr, "rb") as file_input, open(decompr, "wb") as file_output:
        Sc = file_input.read()
        S = lz77_decode(Sc)
        file_output.write(S)

    decompr_size = os.path.getsize(decompr)
    print("Размер после декомпрессии: " + str(decompr_size))
    return k

#k_text=compr_text("ru_text.txt", "compr_ru_text.bin", "decompr_ru_text.txt")
#k_enwik=compr_enwik("enwik7", "compr_ru_enwik.bin", "decompr_ru_enwik.bin")
#k_bin=compr_enwik("random_binary.bin", "compr_ru_bin.bin", "decompr_ru_bin.bin")
#k_bw=compr_enwik("b_w.raw", "compr_image.bin", "decompr_b_w.raw")
#k_gray=compr_enwik("gray.raw", "compr_image.bin", "decompr_gray.raw")
k_color=compr_enwik("color.raw", "compr_image.bin", "decompr_color.raw")

print(f"коэффициент сжатия: {k_color:.3f}")