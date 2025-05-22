import flet as ft
from flet.core.page import Page
from sqlmodel import Session

from model.models import VocabQuiz
from view.top_quiz_history import TopQuizHistory


class ViewWordQuizChecker(ft.View):
    def __init__(self, page: Page, session: Session, top_quiz_history: TopQuizHistory, vocab_quiz: VocabQuiz):
        super().__init__()

        # appbarの設定
        self.appbar = ft.AppBar(title=ft.Text("テスト内容の確認"))

        # 各種情報の設定
        self.page = page
        self.session = session
        self.top_quiz_history = top_quiz_history
        self.vocab_quiz = vocab_quiz

        # テキストフィールドの設定
        self.text_field_quiz_title = ft.TextField(
            label="タイトル",
            width=500,
            value=self.vocab_quiz.title,
            read_only=True
        )
        self.text_field_quiz_description = ft.TextField(
            label="説明文",
            width=500,
            value=self.vocab_quiz.description,
            read_only=True
        )
        self.text_field_quiz_dt = ft.TextField(
            label="実施日",
            width=300,
            value=self.vocab_quiz.quiz_dt.strftime("%Y-%m-%d"),
            read_only=True
        )

        # ボタンの設定
        self.button_submit = ft.ElevatedButton(
            text="テストの新規作成",
            width=200,
            on_click=lambda _: self.event_click_create_vocab_quiz()
        )

        # datatableの設定
        self.data_table_vocab_quiz_data = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("No")),
                ft.DataColumn(ft.Text("単語ID")),
                ft.DataColumn(ft.Text("単語")),
                ft.DataColumn(ft.Text("意味")),
            ]
        )
        self.list_view_vocab_quiz_data = ft.ListView(
            controls=[
                self.data_table_vocab_quiz_data
            ],
            expand=1,
            spacing=10,
            padding=20
        )

        # 行の設定
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
        self.row_text_field_quiz_dt = ft.Row(
            controls=[
                ft.Text("実施日:", width=100),
                self.text_field_quiz_dt
            ],
        )
        self.row_quiz_vocab_quiz_data = ft.Row(
            controls=[
                ft.Container(
                    content=self.list_view_vocab_quiz_data,
                    height=450,
                    width=1000
                ),
            ],
            scroll="auto",
        )
        self.row_button_submit = ft.Row(
            controls=[self.button_submit]
        )

        # controlへの追加
        self.controls = [
            self.row_text_field_quiz_title,
            self.row_text_field_quiz_description,
            self.row_text_field_quiz_dt,
            self.row_quiz_vocab_quiz_data,
            self.row_button_submit
        ]

        # datatableへの行の設定
        self._set_data_table_rows(vocab_quiz)

    #
    # イベントの定義
    #

    def event_click_create_vocab_quiz(self):
        # 新規レコードの追加
        self.session.add(self.vocab_quiz)
        self.session.commit()

        # トップへと戻る
        self.top_quiz_history.back_from_other_view()

    #
    # 各種メソッド
    #

    def _set_data_table_rows(self, vocab_quiz: VocabQuiz):
        rows_list = []

        # 行データの設定
        quiz_data = vocab_quiz.quiz_data["item_list"]

        for index, word_info in enumerate(quiz_data, start=1):
            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(index))),
                    ft.DataCell(ft.Text(word_info["seq_no"])),
                    ft.DataCell(ft.Text(word_info["word"])),
                    ft.DataCell(ft.Text(word_info["meaning"])),
                ]
            )
            rows_list.append(row)

        self.data_table_vocab_quiz_data.rows = rows_list
