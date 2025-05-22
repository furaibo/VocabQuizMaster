import flet as ft
from flet.core.page import Page
from sqlmodel import Session

from model.models import WordBook
from view.top_word_book import TopWordBook


class ViewWordBookCreate(ft.View):
    def __init__(self, page: Page, session: Session, top_word_book: TopWordBook):
        super().__init__()

        # set app bar
        self.appbar = ft.AppBar(title=ft.Text("単語帳情報登録"))

        # 各種情報の設定
        self.page = page
        self.session = session
        self.top_word_book = top_word_book

        # テキストフィールドの設定
        self.text_field_title = ft.TextField(
            label="単語帳名称",
            width=500,
            on_change=lambda _: self.event_check_create_enabled()
        )
        self.text_field_short_name = ft.TextField(
            label="単語帳通称",
            width=500,
        )
        self.text_field_author = ft.TextField(
            label="著者",
            width=500,
        )
        self.text_field_publisher = ft.TextField(
            label="出版社",
            width=500,
        )
        self.text_field_year = ft.TextField(
            label="出版年",
            width=500,
        )
        self.text_field_version = ft.TextField(
            label="バージョン",
            width=500,
        )
        self.text_field_isbn = ft.TextField(
            label="ISBN",
            width=500,
        )
        self.text_field_note = ft.TextField(
            label="備考",
            width=500,
            multiline=True
        )

        # ボタンの設定
        self.button_submit = ft.ElevatedButton(
            text="単語帳情報の新規登録",
            width=500,
            disabled=True,
            on_click=lambda _: self.event_click_create()
        )

        # 行データの設定
        self.row_text_field_title = ft.Row(
            controls=[self.text_field_title],
            spacing=20
        )
        self.row_text_field_short_name = ft.Row(
            controls=[self.text_field_short_name],
            spacing=20
        )
        self.row_text_field_author = ft.Row(
            controls=[self.text_field_author],
            spacing=20
        )
        self.row_text_field_publisher = ft.Row(
            controls=[self.text_field_publisher],
            spacing=20
        )
        self.row_text_field_year = ft.Row(
            controls=[self.text_field_year],
            spacing=20
        )
        self.row_text_field_version = ft.Row(
            controls=[self.text_field_version],
            spacing=20
        )
        self.row_text_field_isbn = ft.Row(
            controls=[self.text_field_isbn],
            spacing=20
        )
        self.row_text_field_note = ft.Row(
            controls=[self.text_field_note],
            spacing=20
        )
        self.row_button_submit = ft.Row(
            controls=[self.button_submit],
            spacing=20
        )

        # controls設定
        self.controls = [
            self.row_text_field_title,
            self.row_text_field_short_name,
            self.row_text_field_author,
            self.row_text_field_publisher,
            self.row_text_field_year,
            self.row_text_field_version,
            self.row_text_field_isbn,
            self.row_text_field_note,
            self.row_button_submit
        ]

    #
    # イベントの定義
    #

    def event_click_create(self):
        # 新規レコードの追加
        word_book = WordBook(
            title=self.text_field_title.value,
            short_name=self.text_field_short_name.value,
            author=self.text_field_author.value,
            publisher=self.text_field_publisher.value,
            year=self.text_field_year.value,
            version=self.text_field_version.value,
            isbn=self.text_field_isbn.value,
            note=self.text_field_note.value,
        )
        self.session.add(word_book)
        self.session.commit()

        # トップへと戻る
        self.top_word_book.back_from_other_view()

    def event_check_create_enabled(self):
        if self.text_field_title.value == "":
            self.button_submit.disabled = True
        else:
            self.button_submit.disabled = False
        self.button_submit.update()

