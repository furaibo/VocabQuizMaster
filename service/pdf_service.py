from pathlib import Path
from sqlmodel import Session, select

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4, portrait
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import mm
from reportlab.lib import colors

from model.models import VocabQuiz


class PdfService:
    def __init__(self, session: Session):
        self.session = session

        # フォントの登録および埋込み処理
        #self.default_font_name = "HeiseiKakuGo-W5"
        #pdfmetrics.registerFont(UnicodeCIDFont(self.default_font_name))
        self.default_font_name = "KosugiMaru-Regular"
        self.default_font_file_path = "data/fonts/KosugiMaru-Regular.ttf"
        pdfmetrics.registerFont(TTFont(self.default_font_name, self.default_font_file_path))


    def save_answer_pdf_file(self, save_file_path: Path, vocab_quiz: VocabQuiz):
        pdf_canvas = canvas.Canvas(str(save_file_path), pagesize=A4)
        self.set_pdf_info(pdf_canvas, vocab_quiz)
        self.print_string_to_pdf(pdf_canvas, vocab_quiz, 0)
        pdf_canvas.save()

    def save_quiz_pdf_file(self, save_file_path: Path, vocab_quiz: VocabQuiz):
        pdf_canvas = canvas.Canvas(str(save_file_path))
        self.set_pdf_info(pdf_canvas, vocab_quiz)
        self.print_string_to_pdf(pdf_canvas, vocab_quiz, 1)
        pdf_canvas.save()

    def set_pdf_info(self, pdf_canvas, vocab_quiz):
        pdf_canvas.setTitle(vocab_quiz.title)
        pdf_canvas.setAuthor(vocab_quiz.author)
        #pdf_canvas.setSubject(subject)

    def print_string_to_pdf(self, pdf_canvas, vocab_quiz: VocabQuiz, mode: int):
        # get quiz count
        quiz_count = len(vocab_quiz.quiz_data["item_list"])

        # サイズの取得(A4準拠)
        #width, height = A4

        # テストタイトルのテキスト表示
        pdf_canvas.setFont(self.default_font_name, 20)
        pdf_canvas.drawString(85, 730, vocab_quiz.title)

        # テスト記述のテキスト表示
        pdf_canvas.setFont(self.default_font_name, 10)
        pdf_canvas.drawString(85, 695, vocab_quiz.description)

        # 実施日時の表示
        quiz_dt_str = vocab_quiz.quiz_dt.strftime("%Y-%m-%d")
        pdf_canvas.setFont(self.default_font_name, 9)
        pdf_canvas.drawString(420, 735, "実施日: " + quiz_dt_str)

        # 得点・氏名記入欄の表示
        pdf_canvas.setFont(self.default_font_name, 10)
        pdf_canvas.setLineWidth(1)
        pdf_canvas.drawString(360, 695, "氏名")
        pdf_canvas.drawString(360, 660, "得点")
        pdf_canvas.drawString(485, 660, "/ " + str(quiz_count))
        pdf_canvas.line(360, 690, 510, 690)
        pdf_canvas.line(360, 655, 510, 655)

        # 単語テスト用のテーブル作成
        # Note: WrapOn/drawOn設定時は表示開始位置の調整が必要
        table_row_list = self._get_table_row_list(vocab_quiz, mode)
        table = Table(table_row_list, colWidths=(10*mm, 40*mm, 100*mm), rowHeights=9*mm, hAlign="LEFT")
        table.setStyle(TableStyle([
            ("FONT", (0, 0), (-1, -1), self.default_font_name, 10),
            ("BOX", (0, 0), (-1, -1), 1, colors.black),
            ("INNERGRID", (0, 0), (-1, -1), 1, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        table.wrapOn(pdf_canvas, 30*mm, (220 - 9 * quiz_count)*mm)
        table.drawOn(pdf_canvas, 30*mm, (220 - 9 * quiz_count)*mm)

    def _get_table_row_list(self, vocab_quiz: VocabQuiz, mode: int):
        row_list = []
        quiz_data = vocab_quiz.quiz_data

        # 単語テスト行の生成
        for index, word_info in enumerate(quiz_data["item_list"], start=1):
            word = word_info["word"]
            meaning = word_info["meaning"]

            # 行設定
            row = []
            if mode == 0:
                row = [index, word, meaning]
            if mode == 1:
                row = [index, word, ""]
            elif mode == 2:
                row = [index, "", meaning]

            row_list.append(row)

        return row_list
