import flet as ft
from flet.core.page import Page

import datetime
from sqlmodel import Session, select

from model.models import VocabQuiz
from view.top_quiz_history import TopQuizHistory


class ViewWordQuizEdit(ft.View):
    def __init__(self, page: Page, session: Session, top_quiz_history: TopQuizHistory, vocab_quiz: VocabQuiz):
        super().__init__()

        # appbarの設定
        self.appbar = ft.AppBar(title=ft.Text("テスト情報の編集"))

        # 各種情報の設定
        self.page = page
        self.session = session
        self.top_quiz_history = top_quiz_history
        self.vocab_quiz = vocab_quiz

        # datepickerの設定
        self.date_picker_quiz_dt = ft.DatePicker(
            first_date=datetime.datetime(year=2020, month=1, day=1),
            on_change=self.event_change_date_pick
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

        # テキストフィールドの設定
        self.text_field_title = ft.TextField(
            label="タイトル",
            width=500,
            value=self.vocab_quiz.title,
            on_change=lambda _: self.event_check_update_enabled()
        )
        self.text_field_description = ft.TextField(
            label="説明文",
            width=500,
            value=self.vocab_quiz.description,
        )
        self.text_field_quiz_dt = ft.TextField(
            label="実施日",
            width=300,
            value=self.vocab_quiz.quiz_dt.strftime("%Y-%m-%d"),
        )

        # ボタンの設定
        self.button_quiz_dt_picker = ft.ElevatedButton(
            "実施日の選択",
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=lambda _: self.page.open(self.date_picker_quiz_dt),
        )
        self.button_submit = ft.ElevatedButton(
            text="内容の更新",
            width=200,
            on_click=lambda _: self.event_click_update()
        )

        # 行の設定
        self.row_text_field_title = ft.Row(
            controls=[
                ft.Text("タイトル:", width=100),
                self.text_field_title],
        )
        self.row_text_field_description = ft.Row(
            controls=[
                ft.Text("説明文:", width=100),
                self.text_field_description
            ],
        )
        self.row_date_picker_quiz_dt = ft.Row(
            controls=[
                ft.Text("実施日:", width=100),
                self.text_field_quiz_dt,
                self.button_quiz_dt_picker
            ],
        )
        self.row_quiz_vocab_quiz_data = ft.Row(
            controls=[
                ft.Container(
                    content=self.list_view_vocab_quiz_data,
                    height=460,
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
            self.row_text_field_title,
            self.row_text_field_description,
            self.row_date_picker_quiz_dt,
            self.row_quiz_vocab_quiz_data,
            self.row_button_submit
        ]

        # datatableへの行の設定
        self._set_data_table_rows(vocab_quiz)

    #
    # イベントの定義
    #

    def event_check_update_enabled(self):
        if self.text_field_title.value == "":
            self.button_submit.disabled = True
        else:
            self.button_submit.disabled = False
        self.button_submit.update()

    def event_change_date_pick(self, e):
        quiz_dt_str = e.control.value.strftime("%Y-%m-%d")
        self.text_field_quiz_dt.value = quiz_dt_str
        self.text_field_quiz_dt.update()

    #
    # 各種メソッド
    #

    def event_click_update(self):
        statement = select(VocabQuiz).where(VocabQuiz.id == self.vocab_quiz.id)
        vocab_quiz = self.session.exec(statement).first()

        # 既存レコードへの値のセット
        vocab_quiz.title = self.text_field_title.value
        vocab_quiz.description = self.text_field_description.value
        vocab_quiz.quiz_dt = self.date_picker_quiz_dt.value

        # 既存レコードの更新
        self.session.add(vocab_quiz)
        self.session.commit()

        # 新規レコードを反映の上、トップに戻る
        self.top_quiz_history.back_from_other_view()

    def _set_data_table_rows(self, vocab_quiz: VocabQuiz):
        rows_list = []

        # 行データの設定
        quiz_data = vocab_quiz.quiz_data

        for index, word_item in enumerate(quiz_data["item_list"], start=1):
            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(index))),
                    ft.DataCell(ft.Text(word_item["seq_no"])),
                    ft.DataCell(ft.Text(word_item["word"])),
                    ft.DataCell(ft.Text(word_item["meaning"])),
                ]
            )
            rows_list.append(row)

        self.data_table_vocab_quiz_data.rows = rows_list
