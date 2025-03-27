import os

def rle(s):
    compressed_data = bytearray()
    n = len(s)
    i = 0
    while i < n:
        current_byte = s[i]
        count = 1
        while i + count < n and count < 255 and s[i + count] == current_byte:
            count += 1
        if count > 1:
            compressed_data.append(count)
            compressed_data.append(current_byte)
            i += count
        else:
            non_repeating = bytearray()
            while i < n and (i + 1 >= n or s[i] != s[i + 1]):
                non_repeating.append(s[i])
                i += 1
                if len(non_repeating) == 255:
                    break
            compressed_data.append(0)
            compressed_data.append(len(non_repeating))
            compressed_data.extend(non_repeating)

    return bytes(compressed_data)


def irle(s):
    decompressed_data = bytearray()
    n = len(s)
    i = 0

    while i < n:
        flag = s[i]
        if flag == 0:
            # Если флаг 0, это неповторяющаяся последовательность
            length = s[i + 1]
            decompressed_data.extend(s[i + 2:i + 2 + length])
            i += 2 + length
        else:
            # Если флаг не 0, это повторяющаяся последовательность
            count = flag
            byte = s[i + 1]
            decompressed_data.extend([byte] * count)
            i += 2

    return bytes(decompressed_data)


def compr_text(input, compr, decompr):#4
    block = 10000
    index=[0]*100000000
    i=0
    bb=0
    result_bwt=b''
    with open(input, "rb") as file_input, open(compr, "wb") as file_output:
        S = file_input.read()
        encoded_rle = rle(S)
        file_output.write(encoded_rle)

    orig_size=os.path.getsize(input)
    compr_size=os.path.getsize(compr)
    print("Размер до сжатия: "+str(orig_size))
    print("Размер после сжатия: "+str(compr_size))
    k=orig_size/compr_size
    i=0
    with open(compr, "rb") as file_input, open(decompr, "w", encoding="utf-8") as file_output:
        Sc = file_input.read()
        S = irle(Sc)
        S = S.decode("utf-8")
        file_output.write(S)

    decompr_size = os.path.getsize(decompr)
    print("Размер после декомпрессии: " + str(decompr_size))
    return k

def compr_enwik(input, compr, decompr):#4
    block = 10000
    index=[0]*100000000
    i=0
    bb=0
    with open(input, "rb") as file_input, open(compr, "wb") as file_output:
        S = file_input.read()
        encoded_rle = rle(S)
        file_output.write(encoded_rle)

    orig_size=os.path.getsize(input)
    compr_size=os.path.getsize(compr)
    print("Размер до сжатия: "+str(orig_size))
    print("Размер после сжатия: "+str(compr_size))
    k=orig_size/compr_size
    i=0
    with open(compr, "rb") as file_input, open(decompr, "wb") as file_output:
        Sc = file_input.read()
        S = irle(Sc)
        file_output.write(S)

    decompr_size = os.path.getsize(decompr)
    print("Размер после декомпрессии: " + str(decompr_size))
    return k


#k_text=compr_text("ru_text.txt", "compr_ru_text.bin", "decompr_ru_text.txt")
#k_bin=compr_enwik("random_binary.bin", "compr_ru_bin.bin", "decompr_ru_bin.bin")
#k_enwik=compr_enwik("enwik7", "compr_ru_enwik.bin", "decompr_ru_enwik.bin")
#k_bw=compr_enwik("b_w.raw", "compr_image.bin", "decompr_b_w.raw")
#k_gray=compr_enwik("gray.raw", "compr_image.bin", "decompr_gray.raw")
k_color=compr_enwik("color.raw", "compr_image.bin", "decompr_color.raw")

print("коэффициент сжатия: "+str(k_color))