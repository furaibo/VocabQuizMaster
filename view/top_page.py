import flet as ft
from pathlib import Path
from configparser import ConfigParser
from sqlmodel import Session, create_engine

from view.top_quiz_generator import TopQuizGenerator
from view.top_quiz_history import TopQuizHistory
from view.top_word_book import TopWordBook
from view.view_word_book_create import ViewWordBookCreate
from view.view_word_book_edit import ViewWordBookEdit
from view.view_word_book_file_importer import ViewWordBookFileImporter
from view.view_word_quiz_checker import ViewWordQuizChecker
from view.view_word_quiz_edit import ViewWordQuizEdit


class TopPage:
    def __init__(self, page: ft.Page, config: ConfigParser, root_path: Path):
        self.page = page
        self.config = config
        self.root_path = root_path

    #
    # メソッド定義
    #

    def init_page(self):
        # トップページ設定
        self.page.title = "単語テスト生成ツール"
        self.page.appbar = ft.AppBar(title=ft.Text("単語テスト生成ツール"))

        # ウィンドウサイズの設定
        self.page.window.width = self.config["window"]["width"]
        self.page.window.height = self.config["window"]["height"]
        self.page.window.min_width = self.config["window"]["min_width"]
        self.page.window.min_height = self.config["window"]["min_height"]

        # 各種変数の初期化
        self.app_route_stack = []
        self.session = self.get_sqlite_session()

        # ページ用Viewイベントの設定
        self.page.on_route_change = self.route_change
        self.page.on_view_pop = self.view_pop
        self.page.go(self.page.route)

        # タブ内部のトップ表示用レイアウト定義
        self.top_quiz_generator = TopQuizGenerator(self.page, self.session)
        self.top_quiz_history = TopQuizHistory(self.page, self.session)
        self.top_word_book = TopWordBook(self.page, self.session)

        # ロケール設定
        self.page.locale_configuration = ft.LocaleConfiguration(
            supported_locales=[ft.Locale("ja", "JP"), ft.Locale("en", "US")],
            current_locale=ft.Locale("ja", "JP")
        )

        # コントロールの設定
        self.set_controls()

        # 更新
        self.page.update()

    def get_sqlite_session(self):
        # sqlite path
        sqlite_path = self.root_path / self.config["sqlite"]["file_path"]
        sqlite_url = f"sqlite:///{sqlite_path}"

        # get engine & session
        engine = create_engine(sqlite_url, echo=True)
        session = Session(engine)
        return session

    #
    # Flet画面制御用メソッドの定義
    #

    def route_change(self, route: str):
        self.app_route_stack.append(route)

        if self.page.route == "/quiz/check":
            vocab_quiz = self.top_quiz_generator.generated_vocab_quiz
            view_word_quiz_checker = ViewWordQuizChecker(self.page, self.session, self.top_quiz_history, vocab_quiz)
            self.page.views.append(view_word_quiz_checker)
        elif self.page.route == "/quiz/edit":
            vocab_quiz = self.top_quiz_history.selected_vocab_quiz
            view_word_quiz_edit = ViewWordQuizEdit(self.page, self.session, self.top_quiz_history, vocab_quiz)
            self.page.views.append(view_word_quiz_edit)
        elif self.page.route == "/wordbook/create":
            view_word_book_create = ViewWordBookCreate(self.page, self.session, self.top_word_book)
            self.page.views.append(view_word_book_create)
        elif self.page.route == "/wordbook/edit":
            word_book = self.top_word_book.selected_word_book
            view_word_book_edit = ViewWordBookEdit(self.page, self.session, self.top_word_book, word_book)
            self.page.views.append(view_word_book_edit)
        elif self.page.route == "/wordbook/importer":
            view_word_book_file_importer = ViewWordBookFileImporter(self.page, self.session, self.top_word_book)
            self.page.views.append(view_word_book_file_importer)

        self.page.update()

    def view_pop(self, view):
        self.page.views.pop()
        self.app_route_stack.pop()

        if len(self.page.views) > 1:
            next_route = self.app_route_stack[-1]
            self.page.route = next_route
            self.page.update()
        else:
            self.page.go("/")

    def set_controls(self):
        # タブ定義
        header_tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="新規テスト作成",
                    icon=ft.Icons.BOOK,
                    content=self.top_quiz_generator
                ),
                ft.Tab(
                    text="作成済テスト一覧",
                    icon=ft.Icons.SEARCH,
                    content=self.top_quiz_history
                ),
                ft.Tab(
                    text="単語帳データ管理",
                    icon=ft.Icons.SETTINGS,
                    content=self.top_word_book
                ),
            ],
            expand=1,
        )

        self.page.controls = [
            header_tabs
        ]
