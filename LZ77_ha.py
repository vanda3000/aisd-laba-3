import os
import numpy
import queue

def lz77_encode(data: bytes, buffer_size: int) -> bytes:
    encoded_data = bytearray()
    i = 0
    n = len(data)

    while i < n:
        max_length = 0
        max_offset = 0

        # Определяем границы поиска
        search_start = max(0, i - buffer_size)
        search_end = i

        # Ищем максимальное совпадение
        for length in range(min(255, n - i), 0, -1):
            substring = data[i:i + length]
            offset = data[search_start:search_end].rfind(substring)
            if offset != -1:
                max_length = length
                max_offset = search_end - search_start - offset
                break

        if max_length > 0:
            # Кодируем offset и length в два байта каждый
            encoded_data.append((max_offset >> 8) & 0xFF)  # Старший байт offset
            encoded_data.append(max_offset & 0xFF)  # Младший байт offset
            encoded_data.append((max_length >> 8) & 0xFF)  # Старший байт length
            encoded_data.append(max_length & 0xFF)  # Младший байт length
            i += max_length
        else:
            # Если совпадений нет, кодируем как символ
            encoded_data.append(0)  # offset = 0 (старший байт)
            encoded_data.append(0)  # offset = 0 (младший байт)
            encoded_data.append(0)  # length = 0 (старший байт)
            encoded_data.append(0)  # length = 0 (младший байт)
            encoded_data.append(data[i])  # символ (1 байт)
            i += 1

    return bytes(encoded_data)


def lz77_decode(encoded_data: bytes) -> bytes:
    decoded_data = bytearray()
    i = 0
    n = len(encoded_data)

    while i < n:
        # Читаем offset и length (по два байта каждый)
        offset = (encoded_data[i] << 8) | encoded_data[i + 1]
        length = (encoded_data[i + 2] << 8) | encoded_data[i + 3]
        i += 4

        if offset == 0 and length == 0:
            # Это символ
            decoded_data.append(encoded_data[i])
            i += 1
        else:
            # Это ссылка
            start = len(decoded_data) - offset
            end = start + length
            decoded_data.extend(decoded_data[start:end])

    return bytes(decoded_data)


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

def compr_text(input, compr, decompr):#4
    b=10240
    with open(input, "rb") as file_input, open(compr, "wb") as file_output:
        S = file_input.read()
        lz=lz77_encode(S, b)
        res_HA, codes = HA(lz)
        file_output.write(res_HA)
    orig_size=os.path.getsize(input)
    compr_size=os.path.getsize(compr)
    print("Размер до сжатия: "+str(orig_size))
    print("Размер после сжатия: "+str(compr_size))
    k=orig_size/compr_size
    with open(compr, "rb") as file_input, open(decompr, "w", encoding="utf-8") as file_output:
        Sc = file_input.read()
        Sha = huffman_decompress(Sc, codes)
        S=lz77_decode(Sha)
        S = S.decode("utf-8")
        file_output.write(S)

    decompr_size = os.path.getsize(decompr)
    print("Размер после декомпрессии: " + str(decompr_size))
    return k

def compr_enwik(input, compr, decompr):#4
    b=1024
    with open(input, "rb") as file_input, open(compr, "wb") as file_output:
        S = file_input.read()
        lz = lz77_encode(S, b)
        res_HA, codes = HA(lz)
        file_output.write(res_HA)
    orig_size = os.path.getsize(input)
    compr_size = os.path.getsize(compr)
    print("Размер до сжатия: "+str(orig_size))
    print("Размер после сжатия: "+str(compr_size))
    k=orig_size/compr_size
    i=0
    with open(compr, "rb") as file_input, open(decompr, "wb") as file_output:
        Sc = file_input.read()
        Sha = huffman_decompress(Sc, codes)
        S = lz77_decode(Sha)
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