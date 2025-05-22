from pathlib import Path

import flet as ft
from sqlmodel import Session, select

from model.models import VocabQuiz
from service.quiz_service import QuizService


class TopQuizHistory(ft.Column):
    def __init__(self, page: ft.Page, session: Session):
        super().__init__()

        # page/sessionの設定
        self.page = page
        self.session = session

        # サービスの初期化
        self.quiz_service = QuizService(self.session)

        # 選択済みwordbook
        self.selected_vocab_quiz = None

        # パス処理用のラムダ式
        self.lambda_quiz_edit = lambda _: self.page.go("/quiz/edit")

        # FilePicker定義
        # Note: appendによるpage追加がないとエラー発生
        self.get_save_folder_dialog = ft.FilePicker(on_result=self.event_select_save_folder_dialog)
        self.page.overlay.append(self.get_save_folder_dialog)

        # datatable/listviewの設定
        self.data_table_quiz_history = ft.DataTable(
            width=1000,
            columns=[
                ft.DataColumn(ft.Text("単語帳", width=120)),
                ft.DataColumn(ft.Text("テスト名", width=120)),
                ft.DataColumn(ft.Text("テスト記述", width=200)),
                ft.DataColumn(ft.Text("作成日時", width=80)),
                ft.DataColumn(ft.Text("詳細", width=50)),
                ft.DataColumn(ft.Text("データ", width=50)),
                ft.DataColumn(ft.Text("削除", width=50)),
            ]
        )
        self.list_view_quiz_history = ft.ListView(
            controls=[
                self.data_table_quiz_history
            ],
            expand=1,
            spacing=10,
            padding=10
        )

        # 行データの設定
        self.row_header = ft.Row(
            controls=[ft.Text("作成済テスト一覧", size=20)],
            spacing=20
        )
        self.row_quiz_list_view = ft.Row(
            controls=[
                ft.Container(
                    content=self.list_view_quiz_history,
                    height=500,
                    width=1150
                ),
            ],
            scroll="auto",
        )

        # controls設定
        self.controls = [
            ft.Divider(height=30),
            self.row_header,
            ft.Divider(height=30),
            self.row_quiz_list_view
        ]
        self._set_data_table_rows()

    #
    # イベント定義
    #

    def event_click_vocab_quiz_edit(self, e):
        self.selected_vocab_quiz = e.control.data
        self.lambda_quiz_edit(e)

    def event_click_file_generate(self, e):
        self.selected_vocab_quiz = e.control.data
        self.get_save_folder_dialog.get_directory_path()

    def event_delete_quiz_and_close_modal(self, vocab_quiz: VocabQuiz, dialog):
        # レコードの削除
        self.session.delete(vocab_quiz)
        self.session.commit()

        # テーブル行の再設定および再描画
        self.data_table_quiz_history.rows = []
        self._set_data_table_rows()
        self.data_table_quiz_history.update()

        self.page.close(dialog)

    def event_click_delete_vocab_quiz(self, e):
        vocab_quiz = e.control.data

        # 保存完了のダイアログ表示
        dialog = ft.AlertDialog(
            content=ft.Text("このテストを削除しますか？"),
            actions=[
                ft.TextButton("Yes", on_click=lambda _: self.event_delete_quiz_and_close_modal(vocab_quiz, dialog)),
                ft.TextButton("No", on_click=lambda _: self.page.close(dialog)),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        self.page.open(dialog)

    def event_select_save_folder_dialog(self, e: ft.FilePickerResultEvent):
        # 選択したフォルダパスの取得
        if e.path:
            # 指定パスへのファイル保存処理
            save_folder_path = Path(e.path)
            self.quiz_service.generate_quiz_zip_file(save_folder_path, self.selected_vocab_quiz)

            # 保存完了のダイアログ表示
            dialog = ft.AlertDialog(
                content=ft.Text("単語テストのzipファイル保存が完了しました"),
                actions=[
                    ft.TextButton("OK", on_click=lambda _: self.page.close(dialog)),
                ],
                actions_alignment=ft.MainAxisAlignment.CENTER,
                on_dismiss=lambda e: self.page.add(ft.Text("Non-modal dialog dismissed")),
            )
            self.page.open(dialog)

        else:
            print("get files canceled!")

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
        statement = select(VocabQuiz)
        vocab_quizzes_list = self.session.exec(statement)

        # 行データの設定
        for vocab_quiz in vocab_quizzes_list:
            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(vocab_quiz.word_book.title)),
                    ft.DataCell(ft.Text(vocab_quiz.title)),
                    ft.DataCell(ft.Text(vocab_quiz.description)),
                    ft.DataCell(ft.Text(vocab_quiz.created_at.strftime('%Y-%m-%d %H:%M'))),
                    ft.DataCell(ft.OutlinedButton(
                        text="編集",
                        data=vocab_quiz,
                        on_click=lambda e: self.event_click_vocab_quiz_edit(e),
                    )),
                    ft.DataCell(ft.OutlinedButton(
                        text="保存",
                        data=vocab_quiz,
                        on_click=lambda e: self.event_click_file_generate(e),
                        disabled=self.page.web
                    )),
                    ft.DataCell(ft.IconButton(
                        icon=ft.Icons.DELETE,
                        data=vocab_quiz,
                        on_click=lambda e: self.event_click_delete_vocab_quiz(e)
                    )),
                ]
            )
            rows_list.append(row)

        self.data_table_quiz_history.rows = rows_list
