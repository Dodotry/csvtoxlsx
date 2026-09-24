#!/usr/bin/env python3
# encoding=utf-8
'''
Author: Dodotry
Date: 2026-09-19 21:16:02
LastEditors: Dodotry
LastEditTime: 2026-09-21 22:27:48
'''
"""应用启动入口。"""
import sys

from PySide6.QtCore import QLocale, QLibraryInfo, QTranslator
from PySide6.QtWidgets import QApplication
from qfluentwidgets import setThemeColor, Theme, FluentTranslator

from .core.logger import setup_logger
from .ui.main_window import MainWindow

MS_BLUE = "#0078D4"


def install_translators(app: QApplication) -> list[QTranslator]:
    translators: list[QTranslator] = []

    ft_translator = FluentTranslator(
        QLocale(QLocale.Language.Chinese, QLocale.Country.China)
    )
    app.installTranslator(ft_translator)
    translators.append(ft_translator)

    qt_translator = QTranslator(app)
    translation_path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    if qt_translator.load("qt_zh_CN.qm", translation_path):
        app.installTranslator(qt_translator)
        translators.append(qt_translator)


    return translators

    
def main() -> None:
    setup_logger()
    app = QApplication(sys.argv)
    app.setApplicationName("CSV 转码 / 转表格工具")
    setThemeColor(MS_BLUE, Theme.LIGHT)

    translators = install_translators(app)  # 变量必须留到 app.exec() 之后

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
