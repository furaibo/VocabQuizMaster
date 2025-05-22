import tempfile
import uuid
import random
import zipfile
from pathlib import Path
from datetime import datetime
from sqlmodel import Session, select

from model.models import VocabQuiz, WordBook, WordItem, WordMeaning, VocabQuizInputParam, WordItemInfo
from service.pdf_service import PdfService
from service.word_book_service import WordBookService


class QuizService:
    def __init__(self, session: Session):
        self.session = session
        self.word_book_service = WordBookService(session)
        self.pdf_service = PdfService(session)

    #
    # 各種メソッド
    #

    def generate_new_quiz_data(self, word_book: WordBook, input_param: VocabQuizInputParam, dry_run=False) -> VocabQuiz:
        # wordinfoのlist取得
        word_item_info_list = self.word_book_service.get_word_item_info_list(word_book, input_param.area)

        # listからランダムで必要な要素を取得したのちにソートする
        sample_list = random.sample(word_item_info_list, input_param.count)
        sample_list = sorted(sample_list, key=lambda x: x.seq_no)

        # json/serialize処理
        item_list = [x.__dict__ for x in sample_list]

        # 最終的なテストの内容を整理
        quiz_data = {
            "count": input_param.count,
            "area": input_param.area,
            "item_list": item_list
        }

        # テストデータの作成
        vocab_quiz = VocabQuiz(
            word_book=word_book,
            uuid=str(uuid.uuid4()),
            title=input_param.title,
            description=input_param.description,
            quiz_dt=input_param.quiz_dt,
            quiz_data=quiz_data,
        )

        # dry_runフラグによる処理分岐
        if dry_run:
            # 結果のみ表示
            print(vocab_quiz)
        else:
            # コミット処理の実行
            self.session.add(vocab_quiz)
            self.session.commit()

        return vocab_quiz

    def generate_quiz_zip_file(self, save_path: Path, vocab_quiz: VocabQuiz):
        # 日時の文字列の取得
        date_str = datetime.now().strftime('%Y%m%d%H%M%S')

        # 一時フォルダの作成
        with tempfile.TemporaryDirectory("w+") as td:
            # 各種ファイルパスの設定
            tmp_save_dir_path = Path(td)
            answer_file_path = tmp_save_dir_path / f"{vocab_quiz.title}_answer.pdf"
            quiz_file_path = tmp_save_dir_path / f"{vocab_quiz.title}_quiz.pdf"

            # PDFファイルの作成および保存
            self.pdf_service.save_answer_pdf_file(answer_file_path, vocab_quiz)
            self.pdf_service.save_quiz_pdf_file(quiz_file_path, vocab_quiz)

            # zipファイル名およびパスの設定
            zip_file_name = date_str + ".zip"
            zip_file_path = save_path / zip_file_name

            # zipファイルの作成
            with zipfile.ZipFile(zip_file_path, "w",
                             compression=zipfile.ZIP_DEFLATED,
                             compresslevel=9) as zf:
                zf.write(answer_file_path, arcname=answer_file_path.name)
                zf.write(quiz_file_path, arcname=quiz_file_path.name)
