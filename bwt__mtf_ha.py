import os
import numpy
import queue

# Класс узла для дерева Хаффмана
class Node():
    def __init__(self, symbol = None, counter = None, left = None, right =None, parent = None):
        self.symbol = symbol
        self.counter = counter
        self.left = left
        self.right = right
        self.parent = parent
    def __lt__(self, other):
        return self.counter < other.counter

def count_symb(S):
    N = len(S)
    counter = numpy.array([0 for _ in range(256)])
    for s in S:
        counter[s] += 1
    return counter

def HA(S):
    C = count_symb(S)
    list_of_leafs = []
    Q = queue.PriorityQueue()
    for i in range(256):
        if C[i] != 0:
            leaf = Node(symbol=i, counter=C[i])
            list_of_leafs.append(leaf)
            Q.put(leaf)
    while Q.qsize() >= 2:
        left_node = Q.get()
        right_node = Q.get()
        parent_node = Node(left=left_node, right=right_node)
        left_node.parent = parent_node
        right_node.parent = parent_node
        parent_node.counter = left_node.counter + right_node.counter
        Q.put(parent_node)
    codes = {}
    for leaf in list_of_leafs:
        node = leaf
        code = ""
        while node.parent is not None:
            if node.parent.left == node:
                code = "0" + code
            else:
                code = "1" + code
            node = node.parent
        codes[leaf.symbol] = code
    coded_message = ""
    for byte in S:
        coded_message += codes[byte]
    padding = 8 - len(coded_message) % 8
    coded_message += '0' * padding
    coded_message = f"{padding:08b}" + coded_message
    bytes_string = bytearray()
    for i in range(0, len(coded_message), 8):
        byte = coded_message[i:i + 8]
        bytes_string.append(int(byte, 2))
    return bytes(bytes_string), codes

def huffman_decompress(compressed_data: bytes, huffman_codes: dict) -> bytes:
    padding = compressed_data[0]
    coded_message = ""
    for byte in compressed_data[1:]:
        coded_message += f"{byte:08b}"
    if padding > 0:
        coded_message = coded_message[:-padding]
    reverse_codes = {v: k for k, v in huffman_codes.items()}
    current_code = ""
    decoded_data = bytearray()
    for bit in coded_message:
        current_code += bit
        if current_code in reverse_codes:
            decoded_data.append(reverse_codes[current_code])
            current_code = ""
    return bytes(decoded_data)


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
    f=b''
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

def mtf(S):
    T = [i for i in range(256)]
    res=b''
    for s in S:
        index = T.index(s)
        res+=bytes([index])
        T.pop(index)
        T.insert(0, s)
    return res

def imtf(S):
    T = [i for i in range(256)]
    S_new = bytearray()
    for s in S:
        i = T[s]
        S_new.append(i)
        T.pop(s)
        T.insert(0,i)
    return bytes(S_new)


def rle(s):
    encoded = bytearray()
    n = len(s)
    i = 0
    while i < n:
        k = 1
        while i + 1 < n and s[i] == s[i + 1] and k < 255:
            k += 1
            i += 1
        encoded.extend([k, s[i]])
        i += 1
    return bytes(encoded)


def irle(s):
    decoded = bytearray()
    n = len(s)
    i = 0
    while i < n:
        k = s[i]
        if i + 1 >= n:
            break
        byte = s[i + 1]
        decoded.extend([byte] * k)
        i += 2
    return bytes(decoded)


def compr_text(input, compr, decompr):#4
    block = 10000
    index=[0]*100000000
    i=0
    bb=0
    with open(input, "rb") as file_input, open(compr, "wb") as file_output:
        encoded_mtf=b''
        while True:
            bb+=block
            S = file_input.read(block)
            if not S:
                break
            result_bwt, index[i] = bwt(S)
            encoded_mtf+= mtf(result_bwt)
            i+=1
        res_HA, codes = HA(encoded_mtf)
        file_output.write(res_HA)

    orig_size=os.path.getsize(input)
    compr_size=os.path.getsize(compr)
    print("Размер до сжатия: "+str(orig_size))
    print("Размер после сжатия: "+str(compr_size))
    k=orig_size/compr_size
    i=0
    with open(compr, "rb") as file_input, open(decompr, "w", encoding="utf-8") as file_output:
        Sc = file_input.read()
        S = b''
        haf=huffman_decompress(Sc, codes)
        j=0
        while j<=bb:
            blocks = haf[j:j+block]
            last_column_BWM = imtf(blocks)
            S+= bwt_inverse(last_column_BWM, index[i])
            j+=block
            i+=1
        S = S.decode("utf-8")
        S.replace('\n\n', '\n')
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
        encoded_mtf = b''
        while True:
            bb += block
            S = file_input.read(block)
            if not S:
                break
            result_bwt, index[i] = bwt(S)
            # print("result_bwt: "+str(result_bwt))
            # print("IND"+str(index))
            encoded_mtf += mtf(result_bwt)

            # print(result_bwt)
            # print(encoded_rle)
            i += 1
        # print("mtf: " + str(encoded_mtf))
        res_HA, codes = HA(encoded_mtf)
        # print("HA: " + str(res_HA))
        file_output.write(res_HA)

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
        haf = huffman_decompress(Sc, codes)
        # print("HA_: "+str(haf))
        # print(str(last_column_BWM) + ' ' + str(index[i]))
        j = 0
        pov = b''
        while j <= bb:
            blocks = haf[j:j + block]
            last_column_BWM = imtf(blocks)
            # print("imtf: " + str(last_column_BWM))
            S += bwt_inverse(last_column_BWM, index[i])
            j += block
            i += 1

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
        encoded_mtf=b''
        while True:
            bb += block * pixel_size
            S = file_input.read(block * pixel_size)
            if not S:
                break
            result_bwt, index[i] = bwt(S)
            encoded_mtf += mtf(result_bwt)
            i += 1

        res_HA, codes = HA(encoded_mtf)
        file_output.write(res_HA)
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
        haf = huffman_decompress(Sc, codes)

        j = 0
        while j <= bb:
            blocks = haf[j:j + block]
            last_column_BWM = imtf(blocks)
            # print("imtf: " + str(last_column_BWM))
            S += bwt_inverse(last_column_BWM, index[i])
            j += block
            i += 1

        file_output.write(S)

    decompr_size = os.path.getsize(decompr)
    print("Размер после декомпрессии: " + str(decompr_size))
    return k


#k_text=compr_text("ru_text.txt", "compr_ru_text.bin", "decompr_ru_text.txt")
#k_enwik=compr_enwik("enwik7", "compr_ru_enwik.bin", "decompr_ru_enwik.bin")
#k_bin=compr_enwik("random_binary.bin", "compr_ru_bin.bin", "decompr_ru_bin.bin")
#k_bw=compr_raw("b_w.raw", "compr_image.bin", "decompr_b_w.raw")
#k_gray=compr_raw("gray.raw", "compr_image.bin", "decompr_gray.raw")
k_color=compr_raw("color.raw", "compr_image.bin", "decompr_color.raw")

print("коэффициент сжатия: "+str(k_color))