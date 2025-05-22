from pathlib import Path

import flet as ft
from flet.core.file_picker import FilePickerFileType
from flet.core.page import Page
from sqlmodel import Session, select

from model.models import WordItem, WordMeaning
from view.top_word_book import TopWordBook
from service.word_book_service import WordBookService


class ViewWordBookFileImporter(ft.View):
    def __init__(self, page: Page, session: Session, top_word_book: TopWordBook):
        super().__init__()

        # set app bar
        self.appbar = ft.AppBar(title=ft.Text("単語データ登録・更新"))

        # 各種情報の設定
        self.page = page
        self.word_book = top_word_book.selected_word_book

        # サービスの初期化
        self.wordbook_service = WordBookService(session)

        # 画像形式
        self.allowed_extensions_list = ["csv"]


        #
        # 各種UIの定義
        #

        # FilePicker定義
        # Note: appendによるpage追加がないとエラー発生
        get_input_file_dialog = ft.FilePicker(on_result=self.event_get_input_file_result)
        self.page.overlay.append(get_input_file_dialog)

        # テキストの設定
        self.text_input_file_load_finished = ft.Text(
            "登録処理が完了しました",
            visible=False
        )

        # テキストフィールドの設定
        self.text_field_word_book_title = ft.TextField(
            label="タイトル",
            width=500,
            value=self.word_book.title,
            read_only=True
        )
        self.text_field_input_file_path = ft.TextField(
            label="読込ファイルパス(CSV形式)",
            width=500,
            read_only=True
        )

        # datatableの設定
        self.data_table_word_item_data = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("No")),
                ft.DataColumn(ft.Text("単語")),
                ft.DataColumn(ft.Text("意味")),
            ]
        )
        self.list_view_word_item_data = ft.ListView(
            controls=[
                self.data_table_word_item_data
            ],
            expand=1,
            spacing=10,
            padding=20
        )

        # ボタンの設定
        self.button_select_input_file_path = ft.FilledButton(
            text="ファイル指定",
            width=150,
            icon=ft.Icons.UPLOAD_FILE,
            on_click=lambda _: get_input_file_dialog.pick_files(
                file_type=FilePickerFileType.CUSTOM,
                allowed_extensions=self.allowed_extensions_list,
            ),
        )
        self.button_input_file_load = ft.FilledButton(
            text="単語データ登録・更新開始",
            width=600,
            disabled=True,
            on_click=lambda _: self.event_start_input_file_load()
        )

        # 行の設定
        self.row_word_book_title = ft.Row(
            controls=[
                ft.Text("対象単語帳", width=100),
                self.text_field_word_book_title
            ]
        )
        self.row_input_file_path = ft.Row(
            controls=[
                ft.Text("対象入力ファイル", width=100),
                self.text_field_input_file_path,
                self.button_select_input_file_path
            ]
        )
        self.row_start_input_file_load = ft.Row(
            controls=[
                self.button_input_file_load,
                self.text_input_file_load_finished
            ]
        )
        self.row_word_book_item_data = ft.Row(
            controls=[
                ft.Container(
                    content=self.list_view_word_item_data,
                    height=480,
                    width=1000
                ),
            ],
            scroll="auto",
        )

        # controlの設定
        self.controls.extend([
            self.row_word_book_title,
            self.row_input_file_path,
            self.row_start_input_file_load,
            self.row_word_book_item_data
        ])

        # datatableへの行の設定
        self._set_data_table_rows()

    #
    # イベントの定義
    #

    def event_get_input_file_result(self, e: ft.FilePickerResultEvent):
        if e.files:
            # ファイルパスの取得
            input_file_path = e.files[0].path
            self.text_field_input_file_path.value = input_file_path
            self.text_field_input_file_path.update()
            self.text_input_file_load_finished.visible = False
            self.text_input_file_load_finished.update()
            self.button_input_file_load.disabled = False
            self.button_input_file_load.update()
        else:
            print("get files canceled!")

    def event_start_input_file_load(self):
        self.button_input_file_load.disabled = False
        self.button_input_file_load.update()

        file_path = Path(self.text_field_input_file_path.value)
        self.wordbook_service.import_wordbook_contents(self.word_book, file_path)

        self.text_input_file_load_finished.visible = True
        self.text_input_file_load_finished.update()

    #
    # 各種メソッド
    #

    def _set_data_table_rows(self):
        rows_list = []

        # 行データの設定
        word_item_info_list = self.wordbook_service.get_word_item_info_list(self.word_book)

        for info in word_item_info_list:
            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(info.seq_no)),
                    ft.DataCell(ft.Text(info.word)),
                    ft.DataCell(ft.Text(info.meaning)),
                ]
            )
            rows_list.append(row)

        self.data_table_word_item_data.rows = rows_list
