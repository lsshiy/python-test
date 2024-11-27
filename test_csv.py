import csv
from typing import List, Dict, Any


class CSVHandler:
    def __init__(self, file_path: str, delimiter: str = ',', encoding: str = 'utf-8'):
        self.file_path = file_path
        self.delimiter = delimiter
        self.encoding = encoding

    def read_all(self) -> List[Dict[str, Any]]:
        """CSVファイルを辞書のリストとして読み込む"""
        try:
            with open(self.file_path, mode='r', encoding=self.encoding) as file:
                reader = csv.DictReader(file, delimiter=self.delimiter)
                return [row for row in reader]
        except FileNotFoundError:
            return []  # ファイルが存在しない場合は空リストを返す

    def append_unique_rows(self, rows: List[Dict[str, Any]], id_column: str = "ID") -> List[Dict[str, Any]]:
        """
        一意の行のみCSVファイルに追加し、追加された新規行を返す

        Args:
            rows (List[Dict[str, Any]]): 追加する候補の行のリスト
            id_column (str): ユニーク性を確認する列名（デフォルトは "ID"）

        Returns:
            List[Dict[str, Any]]: 新規に追加された行のリスト
        """
        existing_data = self.read_all()
        existing_ids = {row[id_column] for row in existing_data if id_column in row and row[id_column]}

        # 新規行をフィルタリング
        new_rows = [row for row in rows if row.get(id_column) not in existing_ids]

        if new_rows:
            # ヘッダーを取得
            fieldnames = existing_data[0].keys() if existing_data else rows[0].keys()
            with open(self.file_path, mode='a', encoding=self.encoding, newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=self.delimiter)
                if file.tell() == 0:  # ファイルが空の場合、ヘッダーを書く
                    writer.writeheader()
                writer.writerows(new_rows)

        return new_rows
