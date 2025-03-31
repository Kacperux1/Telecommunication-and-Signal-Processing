import numpy as np

h_matrix = np.array(
    [[1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
     [1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
     [1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0],
     [0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
     [1, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0],
     [1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0],
     [0, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0],
     [1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1]], dtype=int)


def encode(message):
    result = []
    for char in message:
        binary_char = [int(b) for b in format(ord(char), '08b')]
        even_bits = (np.dot(h_matrix[:, :8], binary_char) % 2).tolist()
        result.append(binary_char + even_bits)
    return result


def is_correct(encoded_message):
    decoded = []
    for codeword in encoded_message:
        syndrome = np.dot(h_matrix, codeword) % 2
        if any(syndrome):
            for i in range(16):
                if np.array_equal(h_matrix[:, i], syndrome):
                    codeword[i] = 1 - codeword[i]
                    break
        decoded.append(codeword[:8])
    return decoded


def decode(coded_message):
    result = []
    for codeword in coded_message:
        binary_char = codeword[:8]
        ascii_char = chr(int(''.join(map(str, binary_char)), 2))
        result.append(ascii_char)
    return ''.join(result)


def main():
    message = "Ala ma kota"
    print(message)
    coded_message = encode(message)
    coded_message[2][6] = 1 - coded_message[2][6]
    coded_message[3][3] = 1 - coded_message[3][3]
    coded_message[1][1] = 1 - coded_message[1][1]
    print(decode(coded_message))
    decoded_message = decode(is_correct(coded_message))
    print(decoded_message)


main()
