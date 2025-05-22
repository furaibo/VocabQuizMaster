import flet as ft
from sqlmodel import Session, select

from model.models import WordBook


class TopWordBook(ft.Column):
    def __init__(self, page: ft.Page, session: Session):
        super().__init__()

        # page/sessionの設定
        self.page = page
        self.session = session

        # パス処理用のラムダ式
        self.lambda_word_book_create = lambda _: self.page.go("/wordbook/create")
        self.lambda_word_book_edit = lambda _: self.page.go("/wordbook/edit")
        self.lambda_word_book_file_importer = lambda _: self.page.go("/wordbook/importer")

        # 選択済みwordbook
        self.selected_word_book = None

        # ボタンの設定
        self.button_create_word_book = ft.ElevatedButton(
            text="単語帳の新規作成",
            width=200,
            on_click=self.lambda_word_book_create
        )

        # datatable/listviewの設定
        self.data_table_word_book = ft.DataTable(
            width=1100,
            columns=[
                ft.DataColumn(ft.Text("ID", width=30), numeric=True),
                ft.DataColumn(ft.Text("名称", width=200)),
                ft.DataColumn(ft.Text("通称", width=80)),
                ft.DataColumn(ft.Text("", width=60)),
                ft.DataColumn(ft.Text("", width=60)),
                ft.DataColumn(ft.Text("削除", width=60)),
            ]
        )
        self.list_view_word_book = ft.ListView(
            controls=[
                self.data_table_word_book
            ],
            expand=1,
            spacing=10,
            padding=10
        )

        # 行データの設定
        self.row_header = ft.Row(
            controls=[ft.Text("単語帳一覧", size=20)],
            spacing=20
        )
        self.row_create_word_book = ft.Row(
            controls=[self.button_create_word_book],
            spacing=20
        )
        self.row_list_view_word_book = ft.Row(
            controls=[
                ft.Container(
                    content=self.list_view_word_book,
                    height=500,
                    width=1150
                ),
            ],
        )

        # controls設定
        self.controls = [
            ft.Divider(height=30),
            self.row_header,
            ft.Divider(height=30),
            self.row_create_word_book,
            self.row_list_view_word_book
        ]

        # datatableへの行の設定
        self._set_data_table_rows()

    #
    # イベント定義
    #

    def event_click_word_book_edit(self, e):
        self.selected_word_book = e.control.data
        self.lambda_word_book_edit(e)

    def event_click_file_importer(self, e):
        self.selected_word_book = e.control.data
        self.lambda_word_book_file_importer(e)

    def event_delete_word_book_and_close_modal(self, word_book: WordBook, dialog):
        # レコードの削除
        self.session.delete(word_book)
        self.session.commit()

        # テーブル行の再設定および再描画
        self._set_data_table_rows()
        self.data_table_word_book.update()

        self.page.close(dialog)

    def event_click_delete_word_book(self, e):
        word_book = e.control.data

        # 保存完了のダイアログ表示
        dialog = ft.AlertDialog(
            content=ft.Text("この単語帳を削除しますか？"),
            actions=[
                ft.TextButton("Yes", on_click=lambda _: self.event_delete_word_book_and_close_modal(word_book, dialog)),
                ft.TextButton("No", on_click=lambda _: self.page.close(dialog)),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        self.page.open(dialog)


    #
    # 各種メソッド
    #

    def back_from_other_view(self):
        self._set_data_table_rows()
        self.page.go("/")
        self.page.views.pop()
        self.page.update()

    def _set_data_table_rows(self):
        rows_list = []

        # WordBookレコードの読み込み
        statement = select(WordBook)
        word_book_list = self.session.exec(statement)

        # 行データの設定
        for word_book in word_book_list:
            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(word_book.id)),
                    ft.DataCell(ft.Text(word_book.title)),
                    ft.DataCell(ft.Text(word_book.short_name)),
                    ft.DataCell(ft.OutlinedButton(
                        text="情報編集",
                        data=word_book,
                        on_click=lambda e: self.event_click_word_book_edit(e),
                    )),
                    ft.DataCell(ft.OutlinedButton(
                        text="単語登録",
                        data=word_book,
                        on_click=lambda e: self.event_click_file_importer(e),
                    )),
                    ft.DataCell(ft.IconButton(
                        icon=ft.Icons.DELETE,
                        data=word_book,
                        on_click=lambda e: self.event_click_delete_word_book(e)
                    )),
                ]
            )
            rows_list.append(row)

        self.data_table_word_book.rows = rows_list
