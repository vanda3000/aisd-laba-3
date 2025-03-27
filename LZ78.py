import os

def lz78_encode(data: bytes) -> bytes:
    dictionary = {b'': 0}
    current_string = b''
    encoded_data = bytearray()

    for byte in data:
        new_string = current_string + bytes([byte])
        if new_string in dictionary:
            current_string = new_string
        else:
            encoded_data.extend(dictionary[current_string].to_bytes(4, 'big'))
            encoded_data.append(byte)
            dictionary[new_string] = len(dictionary)
            current_string = b''

    if current_string:
        encoded_data.extend(dictionary[current_string].to_bytes(4, 'big'))

    return bytes(encoded_data)

def lz78_decode(encoded_data: bytes) -> bytes:
    dictionary = {0: b''}
    decoded_data = bytearray()
    i = 0

    while i < len(encoded_data):
        index = int.from_bytes(encoded_data[i:i + 4], 'big')
        i += 4
        if i < len(encoded_data):
            byte = encoded_data[i]
            i += 1
        else:
            byte = None

        if index in dictionary:
            string = dictionary[index]
            if byte is not None:
                new_string = string + bytes([byte])
                dictionary[len(dictionary)] = new_string
                decoded_data.extend(new_string)
            else:
                decoded_data.extend(string)
        else:
            raise ValueError("Некорректный индекс в закодированных данных")

    return bytes(decoded_data)

def compr_text(input, compr, decompr):#4
    b=1024
    with open(input, "rb") as file_input, open(compr, "wb") as file_output:
        S = file_input.read()
        lz=lz78_encode(S)
        file_output.write(lz)
    orig_size=os.path.getsize(input)
    compr_size=os.path.getsize(compr)
    print("Размер до сжатия: "+str(orig_size))
    print("Размер после сжатия: "+str(compr_size))
    k=orig_size/compr_size
    with open(compr, "rb") as file_input, open(decompr, "w", encoding="utf-8") as file_output:
        Sc = file_input.read()
        S=lz78_decode(Sc)
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

k_text=compr_text("ru_text.txt", "compr_ru_text.bin", "decompr_ru_text.txt")
#k_enwik=compr_enwik("enwik7", "compr_ru_enwik.bin", "decompr_ru_enwik.bin")
#k_bin=compr_enwik("random_binary.bin", "compr_ru_bin.bin", "decompr_ru_bin.bin")
#k_bw=compr_enwik("b_w.raw", "compr_image.bin", "decompr_b_w.raw")
#k_gray=compr_enwik("gray.raw", "compr_image.bin", "decompr_gray.raw")
#k_color=compr_enwik("color.raw", "compr_image.bin", "decompr_color.raw")

print(f"коэффициент сжатия: {k_text:.3f}")