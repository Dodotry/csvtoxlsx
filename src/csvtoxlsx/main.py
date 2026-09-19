#!/usr/bin/env python3
# encoding=utf-8
'''
Author: Dodotry
Date: 2026-09-19 21:16:02
LastEditors: Dodotry
LastEditTime: 2026-09-19 22:20:19
'''
"""应用启动入口。"""

import sys

from PySide6.QtCore import QLocale, QLibraryInfo, QTranslator
from PySide6.QtWidgets import QApplication
from qfluentwidgets import setThemeColor, Theme

from .core.logger import setup_logger, logger
from .ui.main_window import MainWindow

MS_BLUE = "#0078D4"


def _install_translators(app: QApplication) -> None:
    locale = QLocale.system()
    QLocale.setDefault(locale)
    app.setLayoutDirection(locale.textDirection())

    translations_dir = QLibraryInfo.path(QLibraryInfo.TranslationsPath)
    loc_name = locale.name()
    logger.info("系统本地语言: {}", loc_name)
    for prefix in ("qt_", "qtbase_"):
        name = prefix + loc_name
        translator = QTranslator(app)
        if translator.load(name, translations_dir):
            app.installTranslator(translator)
            logger.info("已加载翻译: {}", name)
        else:
            logger.warning("加载翻译失败: {}", name)


def main() -> None:
    setup_logger()

    app = QApplication([])
    app.setApplicationName("CSV 转码 / 转表格工具")
    setThemeColor(MS_BLUE, Theme.LIGHT)
    _install_translators(app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
