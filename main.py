import flet as ft
from pathlib import Path
from configparser import ConfigParser

from view.top_page import TopPage


def get_root_path(dev_mode: bool):
    if dev_mode:
        return Path(__file__).parent
    else:
        # デフォルトパスの設定
        home_path = Path.home()
        folder_name = "vocab_quiz"
        folder_path = home_path / "Documents" / folder_name

        # フォルダの作成
        if not folder_path.exists():
            folder_path.mkdir(parents=True)

        return folder_path


def main(page: ft.Page):
    # get root/config path
    root_path = get_root_path(True)
    config_path = str(root_path / "config.ini")

    # 設定ファイルの取得
    config = ConfigParser()
    config.read(config_path, encoding="utf-8")

    # ページの初期化
    top = TopPage(page, config, root_path)
    top.init_page()


if __name__ == "__main__":
    ft.app(target=main)

