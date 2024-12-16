#pip install p5250

from p5250 import P5250Client

# クライアントオブジェクトを作成
client = P5250Client(
    hostName='your_host_name',  # IBM i システムのホスト名
    path=fr'wc3270.exe',  # wc3270のパス
    codePage='cp930'             # 使用するコードページ
)

# クライアントを接続
if not client.connect():
    print('接続に失敗しました')
    exit(1)

# コマンドを送信 (必要に応じて追加)
client.sendEnter()   # Enterキーを送信
client.sendF(1)      # F1キーを送信
client.sendText("Hello") # テキストを送信

# セッションを終了
client.endSession()
