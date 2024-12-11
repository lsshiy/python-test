# pip install ebcdic
import telnetlib3
import codecs
from ebcdic import EBCDICCodec
import cp930decoder

# CP930のカスタムデコーダーを登録
codecs.register(EBCDICCodec.register)

async def main():
    # CP930をデフォルトのエンコーディングに設定
    reader, writer = await telnetlib3.open_connection(
        'your.ibmi.host', 23,
        encoding='cp930'  # CP930を使用
    )
    try:
        while True:
            data = await reader.read(100)
            print(data)

            # 生バイトデータを取得
            raw_data = await reader.read(100).encode('raw_unicode_escape')
            
            print(f"Raw Data: {raw_data}")

            # エンコーディングを確認
            print(f"現在のエンコーディング: {reader.encoding}")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

# asyncio.runで起動
import asyncio
asyncio.run(main())

# 生データを確認
# data = await reader.read(100)
# print(data.encode('unicode_escape'))  

# import codecs
# data = b'\xaa\xaa\xaa\xaa'
# encoded_data = codecs.encode(data, 'hex') 
# print(encoded_data)

