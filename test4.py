import asyncio
from telnetlib3 import open_connection

async def get_screen(reader):
    """画面の内容を取得してリストとして返す"""
    response = await reader.read(1000)  # サーバーからの応答を取得
    lines = response.splitlines()  # 行ごとに分割してリスト化
    return lines

def get_character_at(lines, row, col):
    """指定した座標の文字を取得"""
    if row < 0 or row >= len(lines):
        raise ValueError("行番号が範囲外です")
    if col < 0 or col >= len(lines[row]):
        raise ValueError("列番号が範囲外です")
    return lines[row][col]  # 指定された座標の文字を返す

async def main():
    # AS/400 接続情報
    host = "192.168.1.100"  # AS/400のIPアドレス
    port = 23  # Telnetのデフォルトポート
    user_id = "YOUR_USERID"  # ユーザーID
    password = "YOUR_PASSWORD"  # パスワード

    # Telnet接続を開始
    reader, writer = await open_connection(host, port)

    try:
        print("接続成功")

        # 初期画面を取得
        initial_screen = await get_screen(reader)
        print("初期画面:")
        print("\n".join(initial_screen))

        # ユーザーIDを送信
        writer.write(user_id + "\r\n")
        await writer.drain()

        # パスワードを送信
        writer.write(password + "\r\n")
        await writer.drain()

        # ログイン後の画面を取得
        screen_after_login = await get_screen(reader)
        print("ログイン後の画面:")
        print("\n".join(screen_after_login))

        # 任意の座標から文字を取得
        row, col = 5, 10  # 取得したい座標（行と列）
        try:
            char_at_position = get_character_at(screen_after_login, row, col)
            print(f"座標 ({row}, {col}) の文字: {char_at_position}")
        except ValueError as e:
            print(f"エラー: {e}")

        # DSPJOBコマンドを送信
        writer.write("DSPJOB\r\n")
        await writer.drain()

        # コマンド実行後の画面を取得
        screen_after_command = await get_screen(reader)
        print("コマンド実行後の画面:")
        print("\n".join(screen_after_command))

        # コマンド後の任意の座標から文字を取得
        row, col = 8, 20  # 別の座標例
        try:
            char_at_position = get_character_at(screen_after_command, row, col)
            print(f"座標 ({row}, {col}) の文字: {char_at_position}")
        except ValueError as e:
            print(f"エラー: {e}")

    except Exception as e:
        print(f"エラー: {e}")
    finally:
        # 接続を終了
        writer.close()
        await writer.wait_closed()
        print("接続を終了しました")

# asyncioループを起動
asyncio.run(main())