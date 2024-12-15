import ebcdic
import codecs
from cp300map import DBCS_MAP

class EBCDIC5026Codec(codecs.Codec):
    def encode(self, input, errors='strict'):
        print("input:",input)
        output = bytearray()
        dbsection = False
        for char in input:
            print(" char:",char)
           
            try:
                # シングルバイトとしてエンコード
                encoded_char = char.encode("cp290", errors=errors)
                if len(encoded_char) == 1:

                    if dbsection == True:
                        # ダブルバイト区間終了
                        output.append(0x0F)
                        dbsection = False
                    print("  => ",r'\x{:02x}'.format(encoded_char[0]))
                    output.append(encoded_char[0])
                else:
                    raise Exception("detected not single byte character: ", encoded_char)
            except UnicodeEncodeError:
                print(" unicode error")
                # ダブルバイトとして解釈
                if dbsection == False:
                    # ダブルバイト区間開始
                    output.append(0x0E)
                    dbsection = True

                # DBCS_MAP からvalがcharのキーを取り出す
                keys = [key for key, value in DBCS_MAP.items() if value == char]
                if len(keys) == 0:
                    raise Exception("key not found:", char)
                elif len(keys) > 1:
                    raise Exception(f"found key is not only one char:{char} keys:{keys}")

                print("  => ",r'\x{:02x}'.format(keys[0][0]))
                print("  => ",r'\x{:02x}'.format(keys[0][1]))
                output.extend(keys[0])

        return bytes(output), len(input)

    def decode(self, input, errors='strict'):
        print("input:", ' '.join(f'{byte:02x}' for byte in input))
        output = []
        dbsection = False
        i = 0
        while i < len(input):
            byte = input[i]
            print("byte:",r'\x{:02x}'.format(byte))
            if byte == 0x0E:
                # ダブルバイト区間開始
                dbsection = True
                i+=1
            elif byte == 0x0F:
                # ダブルバイト区間終了
                dbsection = False
                i+=1
            else:    
                if not dbsection:
                    # シングルバイト
                    print(" => ", bytes([byte]).decode("cp290"))
                    output.append(bytes([byte]).decode("cp290"))
                    i += 1
                else:
                    print("byte:",r'\x{:02x}'.format(input[i + 1]))
                    # ダブルバイト
                    print(" => ", DBCS_MAP[(byte, input[i + 1])])
                    output.append(DBCS_MAP[(byte, input[i + 1])])
                    i += 2
        return ''.join(output), len(input)
    

########################################

# Define the codec registration function
def search_function(name):
    if name == 'cp930':
        return codecs.CodecInfo(
            name='cp930',
            encode=EBCDIC5026Codec().encode,
            decode=EBCDIC5026Codec().decode,
        )
    return None

# Register the codec
codecs.register(search_function)


if __name__ == "__main__":
    print(codecs.decode(bytes([0x62]), "cp290"))

    text = "ABCいろは漢字abc"
    encoded = text.encode("cp930")
    print("encode:",''.join(f'\\b{byte:02x}' for byte in encoded))  # Encoded as bytes in CCSID 5026

    decoded = encoded.decode("cp930")
    print("decode:",decoded)  # Decoded to Unicode string