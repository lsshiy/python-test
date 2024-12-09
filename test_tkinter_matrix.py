import tkinter as tk


class TableApp:
    def __init__(self, master, data):
        """
        コンストラクタ
        :param master: tk.Tkまたはtk.Frameオブジェクト
        :param data: 10x10のデータリスト
        """
        self.master = master
        self.data = data
        self.create_table()

    def create_table(self):
        """
        10x10の表を作成し、コンストラクタで渡されたデータを表示する
        """
        for i in range(10):  # 行
            for j in range(10):  # 列
                value = self.data[i][j] if i < len(self.data) and j < len(self.data[i]) else ""
                label = tk.Label(
                    self.master,
                    text=value,
                    borderwidth=1,
                    relief="solid",
                    width=10,
                    height=2,
                    # anchor="center",
                )
                label.grid(row=i, column=j, sticky="nsew")

        # 列のリサイズを均等に設定
        for j in range(10):
            self.master.grid_columnconfigure(j, weight=1)
        for i in range(10):
            self.master.grid_rowconfigure(i, weight=1)


# サンプルデータを用意
data = [
    [f"{i},{j}" for j in range(10)]  # 10列
    for i in range(10)  # 10行
]
data[3][3] = "3,3 APEJFPQIEHJG+OWIEHNG+SOEIGHNW+EOIGNW+EOIGJNW+OEIGFJNWLEO+IUFHNBWLEIUFHWE"
# アプリを実行
if __name__ == "__main__":
    root = tk.Tk()
    root.title("10x10 Table")
    table = TableApp(root, data)
    root.mainloop()
