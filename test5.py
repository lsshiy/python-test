# Single-byte character map (partial example)
SBCS_MAP = {
    0x41: "A",  # Example: EBCDIC 'A'
    0x42: "B",
    0x43: "C",
    0xA1: "あ",  # Hiragana 'a'
    0xA2: "い",  # Hiragana 'i'
    0xB1: "ア",  # Katakana 'a'
    0xB2: "イ",  # Katakana 'i'
    # ... add more mappings
}

# Double-byte character map (partial example)
DBCS_MAP = {
    (0x42, 0xA1): "漢",  # Kanji '漢'
    (0x42, 0xA2): "字",  # Kanji '字'
    # ... add more mappings
}

###############################

import codecs

class EBCDIC5026Codec(codecs.Codec):
    def encode(self, input, errors='strict'):
        output = bytearray()
        for char in input:
            # Encode single-byte characters
            for key, value in SBCS_MAP.items():
                if value == char:
                    output.append(key)
                    break
            else:
                # Encode double-byte characters
                for (key1, key2), value in DBCS_MAP.items():
                    if value == char:
                        output.extend([key1, key2])
                        break
                else:
                    if errors == 'strict':
                        raise UnicodeEncodeError("ccsid5026", char, 0, 1, "character not found")
                    elif errors == 'replace':
                        output.append(0x3F)  # Replace with '?'
        return bytes(output), len(input)

    def decode(self, input, errors='strict'):
        output = []
        i = 0
        while i < len(input):
            byte = input[i]
            if byte in SBCS_MAP:
                # Decode single-byte characters
                output.append(SBCS_MAP[byte])
                i += 1
            elif i + 1 < len(input) and (byte, input[i + 1]) in DBCS_MAP:
                # Decode double-byte characters
                output.append(DBCS_MAP[(byte, input[i + 1])])
                i += 2
            else:
                # Handle unknown bytes
                if errors == 'strict':
                    raise UnicodeDecodeError("ccsid5026", input, i, i + 1, "byte not found")
                elif errors == 'replace':
                    output.append('?')
                i += 1
        return ''.join(output), len(input)
    

########################################


import codecs

# Define the codec registration function
def search_function(name):
    if name == 'ccsid5026':
        return codecs.CodecInfo(
            name='ccsid5026',
            encode=EBCDIC5026Codec().encode,
            decode=EBCDIC5026Codec().decode,
        )
    return None

# Register the codec
codecs.register(search_function)

##
text = "Aあア漢字"
encoded = text.encode("ccsid5026")
print(encoded)  # Encoded as bytes in CCSID 5026


##

encoded_data = b'\x41\xa1\xb1\x42\xa1\x42\xa2'  # Example CCSID 5026 bytes
decoded = encoded_data.decode("ccsid5026")
print(decoded)  # Decoded to Unicode string

##
import codecs
print(codecs.lookup('ccsid5026'))  # Should not raise an error


##
# Encoding with error handling
text = "Invalid漢字"
encoded = text.encode("ccsid5026", errors="replace")  # Replace invalid characters
print(encoded)

# Decoding with error handling
decoded = b'\x41\xFF'.decode("ccsid5026", errors="ignore")  # Ignore invalid bytes
print(decoded)