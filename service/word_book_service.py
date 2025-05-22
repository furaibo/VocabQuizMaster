import csv
from pathlib import Path
from sqlmodel import Session, select, func

from model.models import WordType, WordBook, WordItem, WordMeaning, WordSentence, WordItemInfo


class WordBookService:
    def __init__(self, session: Session):
        self.session = session

        # word type文字列参照用のdict生成
        self.word_type_str_dict = {}
        statement = select(WordType)
        word_types = self.session.exec(statement)
        for word_type in word_types:
            self.word_type_str_dict[word_type.id] = word_type.title_short_jp

    #
    # 各種メソッド
    #

    def get_jp_word_type_id(self, word_type: str):
        if word_type == "":
            return None

        conv_dict = {
            "名詞": 1,
            "代名詞": 2,
            "動詞": 3,
            "形容詞": 4,
            "副詞": 5,
            "助動詞": 6,
            "前置詞": 7,
            "冠詞": 8,
            "間投詞": 9,
            "接続詞": 10,
            "句動詞": 20,
            "熟語": 30,
            "その他": 99,
        }
        return conv_dict[word_type]

    def get_word_book_list(self):
        statement = select(WordBook)
        word_book_list = self.session.exec(statement)
        return word_book_list

    def get_max_word_seq_no(self, word_book_id):
        statement = select(func.max(WordItem.seq_no)).where(WordItem.word_book_id == word_book_id)
        max_word_seq_no = self.session.exec(statement).first()
        return max_word_seq_no

    def create_word_book(self, info: dict):
        # 単語帳情報の登録
        word_book = WordBook(
            title=info["title"],
            description=info["description"],
            author=info["author"],
            year=info["year"],
            publisher=info["publisher"],
            isbn=info["isbn"],
            note=info["note"],
        )
        self.session.add(word_book)

    def delete_wordbook(self, word_book: WordBook):
        self.session.delete(word_book)
        self.session.commit()

    def get_word_item_info_list(self, word_book: WordBook, area_list: list=[]):
        all_word_items_list = []

        if len(area_list) == 0:
            # 単語帳に紐づくすべての単語アイテム取得
            statement = select(WordItem).join(WordMeaning).where(WordItem.word_book_id == word_book.id)
            fetch_word_items = self.session.exec(statement)
            all_word_items_list.extend(fetch_word_items)
        else:
            for area in area_list:
                lower, upper = area[0], area[1]
                statement = (select(WordItem).join(WordMeaning)
                             .where(WordItem.word_book_id == word_book.id)
                             .where(lower <= WordItem.id)
                             .where(WordItem.id <= upper))
                fetch_word_items = self.session.exec(statement)
                all_word_items_list.extend(fetch_word_items)

        # 各単語アイテムの詳細のdictを作成
        word_item_info_dict = {}
        for word_item in all_word_items_list:
            word_item_id = word_item.id

            if word_item_id not in word_item_info_dict:
                meaning_str_list = []

                for m in word_item.word_meanings:
                    # 意味の文字列を作成
                    word_type_str = self.word_type_str_dict[m.word_type]
                    word_meaning = m.meaning

                    # 複数品詞情報がある場合に対応する
                    if m.sub_word_type is not None:
                        sub_word_type_str = self.word_type_str_dict[m.sub_word_type]
                        tmp_str = "[{0}/{1}]{2}".format(word_type_str, sub_word_type_str, word_meaning)
                        meaning_str_list.append(tmp_str)
                    else:
                        tmp_str = "[{0}]{1}".format(word_type_str, word_meaning)
                        meaning_str_list.append(tmp_str)

                # 1つの連続した文字列としてlist内の要素を連結する
                meaning_str = ", ".join(meaning_str_list)
                word_item_info = WordItemInfo(
                    word_item_id=word_item_id,
                    seq_no=word_item.seq_no,
                    word=word_item.word,
                    meaning=meaning_str
                )
                word_item_info_dict[word_item_id] = word_item_info

        # dict形式からlistに変更する
        word_item_info_list = list(word_item_info_dict.values())

        return word_item_info_list

    def import_wordbook_contents(self, word_book: WordBook, csv_file_path: Path):
        # 単語帳情報の取得及び登録
        with open(csv_file_path, "r", encoding="utf-8") as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=",")

            # CSV1行あたりの処理実行
            for row in csv_reader:
                if row["word"] == "":
                    continue

                # 単語アイテムおよび意味情報・例文情報の追加
                word_item = WordItem(
                    word_book_id=word_book.id,
                    word=row["word"],
                    seq_no=int(row["seq_no"]),
                    section_no=row["section_no"],
                    section_title=row["section_title"],
                    pronunciation=row["pronunciation"],
                    pronunciation_kana=row["pronunciation_kana"],
                )

                # WordItemのID確定のためコミット処理
                self.session.add(word_item)
                self.session.commit()
                self.session.refresh(word_item)

                # 意味情報の追加
                for i in range(1, 4):
                    col_name1 = f"word_type{i}"
                    col_name2 = f"word_meaning{i}"
                    col_name3 = f"note{i}"

                    word_type_list = [x.strip() for x in row[col_name1].split(",")]
                    word_type = word_type_list[0]
                    sub_word_type = word_type_list[1] if len(word_type_list) > 1 else ""
                    meaning = row[col_name2].strip()
                    note = row[col_name3].strip()

                    if meaning != "" and word_type != "":
                        word_meaning = WordMeaning(
                            seq_no=i,
                            word_item_id=word_item.id,
                            word_type=self.get_jp_word_type_id(word_type),
                            sub_word_type=self.get_jp_word_type_id(sub_word_type),
                            meaning=meaning,
                            note=note,
                        )
                        self.session.add(word_meaning)

                # 例文情報の追加
                for i in range(1, 3):
                    col_name1 = f"sentence{i}"
                    col_name2 = f"sentence_translation{i}"

                    sentence = row[col_name1].strip()
                    translation = row[col_name2].strip()

                    if sentence != "" and translation != "":
                        word_sentence = WordSentence(
                            word_item_id=word_item.id,
                            seq_no=i,
                            sentence=sentence,
                            translation=translation
                        )
                        self.session.add(word_sentence)

                # コミット処理
                self.session.commit()
