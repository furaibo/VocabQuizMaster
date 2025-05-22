import csv
from pathlib import Path
from sqlmodel import SQLModel, Session, create_engine
from model.models import WordType

# SQLite用DBファイルパスの設定
sqlite_file_path = Path("data", "database.db")
sqlite_url = f"sqlite:///{sqlite_file_path}"

# マスターファイルパスの設定
master_folder_path = Path("data/seed")
word_types_csv_path = master_folder_path / "word_types.csv"

# エンジンの取得
engine = create_engine(sqlite_url, echo=True)

# テーブルの初期化処理
SQLModel.metadata.create_all(engine)

# セッションの取得
session = Session(engine)

# マスターデータの投入
# 単語タイプ
with open(word_types_csv_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        word_type = WordType(
            id=int(row["id"]),
            title_jp=row["title_jp"],
            title_en=row["title_en"],
            title_short_jp=row["title_short_jp"],
            title_short_en=row["title_short_en"],
        )
        session.add(word_type)

# コミット処理
session.commit()
