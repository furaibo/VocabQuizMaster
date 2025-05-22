import flet as ft
from flet.core.textfield import KeyboardType, NumbersOnlyInputFilter
from sqlmodel import Session, select
import datetime

from model.models import WordBook, VocabQuizInputParam
from service.quiz_service import QuizService
from service.word_book_service import WordBookService


class TopQuizGenerator(ft.Column):
    def __init__(self, page: ft.Page, session: Session):
        super().__init__()

        # page/sessionの設定
        self.page = page
        self.session = session

        # サービスの初期化
        self.quiz_service = QuizService(self.session)
        self.word_book_service = WordBookService(self.session)

        # パス処理用のラムダ式
        self.lambda_quiz_check = lambda _: self.page.go("/quiz/check")

        # 生成済みテストデータ
        self.generated_vocab_quiz = None

        # datepickerの設定
        self.date_picker_quiz_dt = ft.DatePicker(
            first_date=datetime.datetime(year=2020, month=1, day=1),
            on_change=self.event_change_date_pick
        )

        # テキストフィールドの設定
        self.text_field_quiz_title = ft.TextField(
            label="テストタイトル設定",
            width=600,
            on_change=lambda _: self._check_all_input_values()
        )
        self.text_field_quiz_description = ft.TextField(
            label="テスト説明文設定",
            width=600
        )
        self.text_field_quiz_area_from = ft.TextField(
            label="出題範囲(from)",
            width=180,
            keyboard_type=KeyboardType.NUMBER,
            input_filter=NumbersOnlyInputFilter(),
            on_change=lambda _: self._check_all_input_values()
        )
        self.text_field_quiz_area_to = ft.TextField(
            label="出題範囲(to)",
            width=180,
            keyboard_type=KeyboardType.NUMBER,
            input_filter=NumbersOnlyInputFilter(),
            on_change=lambda _: self._check_all_input_values()
        )
        self.text_field_quiz_area_limit = ft.TextField(
            label="指定可能範囲の上限",
            width=180,
            value="-",
            read_only=True
        )
        self.text_field_quiz_dt = ft.TextField(
            label="実施日",
            width=200,
            on_change=lambda _: self._check_all_input_values()
        )

        # ドロップダウンメニューの設定
        self.dropdown_word_book = ft.Dropdown(
            border=ft.InputBorder.UNDERLINE,
            label="単語帳の名称",
            width=500,
            options=self._get_dropdown_word_book_options(),
            on_change=lambda e: self.event_select_word_book(e)
        )
        self.dropdown_quiz_count = ft.Dropdown(
            border=ft.InputBorder.UNDERLINE,
            label="出題単語数",
            width=400,
            options=self._get_dropdown_quiz_count(),
            on_change=lambda _: self._check_all_input_values()
        )

        # ボタンの設定
        self.button_quiz_dt_picker = ft.ElevatedButton(
            "実施日の選択",
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=lambda _: self.page.open(self.date_picker_quiz_dt),
        )
        self.button_dropdown_word_book_update = ft.ElevatedButton(
            "情報更新",
            width=80,
            on_click=lambda e: self.event_click_word_book_update(e)
        )
        self.button_generate_quiz = ft.ElevatedButton(
            text="テスト生成処理の実行",
            width=720,
            disabled=True,
            on_click=lambda e: self.event_click_generate_quiz(e)
        )

        # 行データの設定
        self.row_header = ft.Row(
            controls=[ft.Text("新規テスト設定", size=20)],
            spacing=20
        )
        self.row_text_field_quiz_title = ft.Row(
            controls=[
                ft.Text("タイトル:", width=100),
                self.text_field_quiz_title],
        )
        self.row_text_field_quiz_description = ft.Row(
            controls=[
                ft.Text("説明文:", width=100),
                self.text_field_quiz_description
            ],
        )
        self.row_dropdown_word_book = ft.Row(
            controls=[
                ft.Text("単語帳選択:", width=100),
                self.dropdown_word_book,
                self.button_dropdown_word_book_update
            ],
            spacing=20,
        )
        self.row_text_field_area_from_to = ft.Row(
            controls=[
                ft.Text("出題範囲:", width=100),
                self.text_field_quiz_area_from,
                ft.Text("～"),
                self.text_field_quiz_area_to,
                self.text_field_quiz_area_limit
            ],
        )
        self.row_dropdown_quiz_count = ft.Row(
            controls=[
                ft.Text("出題単語数:", width=100),
                self.dropdown_quiz_count
            ],
        )
        self.row_date_picker_quiz_dt = ft.Row(
            controls=[
                ft.Text("テスト実施日:", width=100),
                self.text_field_quiz_dt,
                self.button_quiz_dt_picker
            ],
        )
        self.row_button_generate_quiz = ft.Row(
            controls=[self.button_generate_quiz],
        )

        # controls設定
        self.controls = [
            ft.Divider(height=30),
            self.row_header,
            ft.Divider(height=30),
            self.row_dropdown_word_book,
            self.row_text_field_quiz_title,
            self.row_text_field_quiz_description,
            self.row_text_field_area_from_to,
            self.row_dropdown_quiz_count,
            self.row_date_picker_quiz_dt,
            ft.Divider(height=30),
            self.row_button_generate_quiz
        ]

    #
    # イベント定義
    #

    def event_select_word_book(self, e):
        word_book_id = e.control.value
        max_word_seq_no = self.word_book_service.get_max_word_seq_no(word_book_id)
        self.text_field_quiz_area_limit.value = max_word_seq_no
        self.text_field_quiz_area_limit.update()
        self._check_all_input_values()

    def event_change_date_pick(self, e):
        quiz_dt_str = e.control.value.strftime("%Y-%m-%d")
        self.text_field_quiz_dt.value = quiz_dt_str
        self.text_field_quiz_dt.update()

    def event_click_word_book_update(self, e):
        self.dropdown_word_book.options = self._get_dropdown_word_book_options()
        self.dropdown_word_book.update()

    def event_click_generate_quiz(self, e):
        self._generate_new_quiz()
        self.lambda_quiz_check(e)

    #
    # 各種メソッド
    #

    def back_from_other_view(self):
        self._clear_all_input_values()
        self.page.go("/")
        self.page.views.pop()
        self.page.update()

    #
    # privateメソッド
    #

    def _clear_all_input_values(self):
        self.text_field_quiz_title.value = ""
        self.text_field_quiz_description.value = ""
        self.text_field_quiz_area_from.value = ""
        self.text_field_quiz_area_to.value = ""
        self.dropdown_word_book.value = ""
        self.dropdown_quiz_count.value = ""

    def _get_dropdown_word_book_options(self):
        statement = select(WordBook)
        word_book_list = self.session.exec(statement)

        options = []
        for word_book in word_book_list:
            option = ft.DropdownOption(
                key=word_book.id,
                text=word_book.title,
            )
            options.append(option)

        return options

    def _get_dropdown_quiz_count(self):
        options = []
        count_list = [10, 20, 30, 40]

        # 単語テスト作成時選択可能な単語数オプションの設定
        for count in count_list:
            option = ft.DropdownOption(key=str(count))
            options.append(option)

        return options

    def _check_all_input_values(self):
        # 空の入力項目がないかのチェック
        flag_not_empty_1 = self.text_field_quiz_title.value != ""
        flag_not_empty_2 = self.dropdown_quiz_count.value != ""
        flag_not_empty_3 = self.date_picker_quiz_dt.value != ""
        flag_not_empty_4 = self.text_field_quiz_area_from.value != ""
        flag_not_empty_5 = self.text_field_quiz_area_to.value != ""
        flag_not_empty_6 = self.dropdown_quiz_count.value != ""

        flag_area_valid = False
        if flag_not_empty_4 and flag_not_empty_5:
            flag_area_valid = int(self.text_field_quiz_area_to.value) > int(self.text_field_quiz_area_from.value)

        # ボタン有効化できるかの判定
        if flag_not_empty_1 and flag_not_empty_2 and flag_not_empty_3 \
                and flag_not_empty_4 and flag_not_empty_5 and flag_not_empty_6 \
                and flag_area_valid:
            self.button_generate_quiz.disabled = False
        else:
            self.button_generate_quiz.disabled = True

        self.row_button_generate_quiz.update()

    def _generate_new_quiz(self):
        # WordBookの取得
        statement = select(WordBook).where(WordBook.id == self.dropdown_word_book.value)
        word_book = self.session.exec(statement).first()

        # テスト生成用のdictの作成
        vocab_quiz_input_param = VocabQuizInputParam(
            title=self.text_field_quiz_title.value,
            description=self.text_field_quiz_description.value,
            count=int(self.dropdown_quiz_count.value),
            quiz_dt=self.date_picker_quiz_dt.value,
            area=[(int(self.text_field_quiz_area_from.value), int(self.text_field_quiz_area_to.value))],
        )

        # 単語テスト内部データの作成
        vocab_quiz = self.quiz_service.generate_new_quiz_data(word_book, vocab_quiz_input_param, dry_run=True)

        # 作成済みテストデータの設定
        self.generated_vocab_quiz = vocab_quiz
