import os


def suffix_array(S):
    n = len(S)
    suffixes = sorted((S[i:], i) for i in range(n+1))
    return [suffix[1] for suffix in suffixes]

def bwt(s):
    n = len(s)
    sa = sorted(range(n), key=lambda i: s[i:] + s[:i])
    last_column = bytearray()
    for i in sa:
        last_column.append(s[(i - 1) % n])
    s_index = sa.index(0)
    return bytes(last_column), s_index

def bwt_inverse(bwt, index):
    N = len(bwt)
    #print("BWT_INV: "+str(bytes(bwt)))
    P_inverse = counting_sort_arg(bwt)
    S = b""
    j = index
    for _ in range(N):
        j = P_inverse[j]
        S = S + bytes([bwt[j]])
    #print("2 BWT_INV: " + str(bytes(S)))
    return bytes(S)


def counting_sort_arg(S):
    N = len(S)
    M = 1114112
    T = [0 for _ in range(M)]
    T_sub = [0 for _ in range(M)]
    for s in S:
        T[s] += 1
    for j in range(1,M):
        T_sub[j] = T_sub[j-1] + T[j-1]
    P = [-1 for _ in range(N)]
    P_inverse = [-1 for _ in range(N)]
    for i in range(N):
        P_inverse[T_sub[S[i]]] = i
        P[i] = T_sub[S[i]]
        T_sub[S[i]] +=1
    return P_inverse

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
        while True:
            bb+=block
            S = file_input.read(block)
            #print("ИСХОДНЫй текст: "+str(S))
            if not S:
                break
            res, index[i] = bwt(S)
            result_bwt+=res
            #print("IND"+str(index))
            #print(result_bwt)
            #print(encoded_rle)
            i+=1
        encoded_rle = rle(result_bwt)
        file_output.write(encoded_rle)

    orig_size=os.path.getsize(input)
    compr_size=os.path.getsize(compr)
    print("Размер до сжатия: "+str(orig_size))
    print("Размер после сжатия: "+str(compr_size))
    k=orig_size/compr_size
    i=0
    with open(compr, "rb") as file_input, open(decompr, "w", encoding="utf-8") as file_output:
        Sc = file_input.read()
        # print(Sc)
        S = b''
        #print(Sc)
        last_column_BWM = irle(Sc)
        #print(str(last_column_BWM) + ' ' + str(index[i]))
        j=0
        while j<=bb:
            blocks = last_column_BWM[j:j+block]
            S+= bwt_inverse(blocks, index[i])
            j+=block
            i+=1

        S = S.decode("utf-8")
        file_output.write(S)
        i += 1

    decompr_size = os.path.getsize(decompr)
    print("Размер после декомпрессии: " + str(decompr_size))
    return k

def compr_enwik(input, compr, decompr):#4
    block = 10000
    index=[0]*100000000
    i=0
    bb=0
    with open(input, "rb") as file_input, open(compr, "wb") as file_output:
        while True:
            bb+=block
            S = file_input.read(block)
            #print("ИСХОДНЫй текст: "+str(S))
            if not S:
                break
            result_bwt, index[i] = bwt(S)
            #print("IND"+str(index))
            encoded_rle = rle(result_bwt)
            file_output.write(encoded_rle)


            #print(result_bwt)
            #print(encoded_rle)
            i+=1

    orig_size=os.path.getsize(input)
    compr_size=os.path.getsize(compr)
    print("Размер до сжатия: "+str(orig_size))
    print("Размер после сжатия: "+str(compr_size))
    k=orig_size/compr_size
    i=0
    with open(compr, "rb") as file_input, open(decompr, "wb") as file_output:
        Sc = file_input.read()
        # print(Sc)
        S = b''
        #print(Sc)
        last_column_BWM = irle(Sc)
        #print(str(last_column_BWM) + ' ' + str(index[i]))
        j=0
        while j<=bb:
            blocks = last_column_BWM[j:j+block]
            S+= bwt_inverse(blocks, index[i])
            j+=block
            i+=1

        file_output.write(S)
        i += 1

    decompr_size = os.path.getsize(decompr)
    print("Размер после декомпрессии: " + str(decompr_size))
    return k


def compr_raw(input, compr, decompr):
    block=10000
    index = [0] * 100000000
    i = 0
    bb = 0

    with open(input, "rb") as file_input, open(compr, "wb") as file_output:
        # Чтение метаданных RAW формата
        color_type = file_input.read(3).decode("ascii")
        width = int.from_bytes(file_input.read(4), byteorder="little")
        height = int.from_bytes(file_input.read(4), byteorder="little")

        # Запись метаданных в сжатый файл
        file_output.write(color_type.encode("ascii"))
        file_output.write(width.to_bytes(4, byteorder="little"))
        file_output.write(height.to_bytes(4, byteorder="little"))

        # Определяем размер пикселя (1 байт для ч/б и серого, 3 байта для цвета)
        pixel_size = 1 if color_type in ["BW ", "GRY"] else 3

        while True:
            bb += block * pixel_size
            S = file_input.read(block * pixel_size)

            if not S:
                break

            result_bwt, index[i] = bwt(S)
            encoded_rle = rle(result_bwt)
            file_output.write(encoded_rle)

            i += 1

    orig_size = os.path.getsize(input)
    compr_size = os.path.getsize(compr)
    print(f"Размер до сжатия: {orig_size}")
    print(f"Размер после сжатия: {compr_size}")
    k = orig_size / compr_size

    i = 0
    with open(compr, "rb") as file_input, open(decompr, "wb") as file_output:
        # Чтение метаданных из сжатого файла
        color_type = file_input.read(3).decode("ascii")
        width = int.from_bytes(file_input.read(4), byteorder="little")
        height = int.from_bytes(file_input.read(4), byteorder="little")

        # Запись метаданных в восстановленный файл
        file_output.write(color_type.encode("ascii"))
        file_output.write(width.to_bytes(4, byteorder="little"))
        file_output.write(height.to_bytes(4, byteorder="little"))

        Sc = file_input.read()
        S = b''
        last_column_BWM = irle(Sc)

        j = 0
        while j <= bb:
            blocks = last_column_BWM[j:j + block * pixel_size]
            S += bwt_inverse(blocks, index[i])
            j += block * pixel_size
            i += 1

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