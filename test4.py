#https://www.mm2d.net/main/legacy/c/c-06.html
import asyncio
import telnetlib3
from pyte import Screen, Stream

async def connect_and_operate(host, port, username, password):
    screen = Screen(80, 24)
    stream = Stream(screen)

    async with telnetlib3.open_connection(
        host=host,
        port=port,
        encoding='ascii',
    ) as conn:
        print("Connected to the host")

        async for data in conn:
            if data:
                stream.feed(data)
                print("\n".join(screen.display))

            # ログイン処理
            if "login:" in data.lower():
                await conn.send(username + "\n")
            elif "password:" in data.lower():
                await conn.send(password + "\n")

            # ログイン後の操作例
            elif "command line" in data.lower():  # 任意のトリガー条件
                # カーソルを動かす
                await conn.send("\x1B[10;20H")  # カーソルを 10行20列に移動（例） ASCIIコード(hex)で1b=>ESC
                
                # テキストを入力
                await conn.send("HELLO IBM i")

                # Enter キーを押す
                await conn.send("\x0D")
                break  # 必要に応じてループを終了

# 接続設定
host = "ibm-host.example.com"
port = 23
username = "your-username"
password = "your-password"

asyncio.run(connect_and_operate(host, port, username, password))
