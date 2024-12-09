import codecs

class CP930Decoder(codecs.Codec):
    def __init__(self):
        # CP290とCP300のマッピングをロード（簡略化例）
        self.cp290 = codecs.getdecoder('cp290')
        self.cp300 = codecs.getdecoder('cp300')
        self.current_decoder = self.cp290  # 初期状態はCP290

    def decode(self, input, errors='strict'):
        output = []
        i = 0
        while i < len(input):
            char = input[i]
            if char == 0x0E:  # SO (Shift Out) マルチバイトモード開始
                self.current_decoder = self.cp300
                i += 1
            elif char == 0x0F:  # SI (Shift In) シングルバイトモード開始
                self.current_decoder = self.cp290
                i += 1
            else:
                decoded_char, _ = self.current_decoder(bytes([char]), errors)
                output.append(decoded_char)
                i += 1
        return ''.join(output), len(input)

# カスタムエンコーディングの登録
def cp930_search(encoding_name):
    if encoding_name == 'cp930':
        return codecs.CodecInfo(
            name='cp930',
            encode=None,  # エンコードは省略
            decode=CP930Decoder().decode
        )
codecs.register(cp930_search)

# import codecs
# data = b'\xaa\xaa\xaa\xaa'
# encoded_data = codecs.encode(data, 'hex') 
# print(encoded_data)
