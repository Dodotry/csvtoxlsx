"""主窗口界面模块。

使用 PySide6-Fluent-Widgets 构建，扁平化现代风格：
- 第一行：标签 + 地址栏 + 浏览按钮 + 转换按钮
- 第二行：转码/转表格 两个单选按钮 + 进度条 + 输出目录设置
- 下方：信息框（实时显示处理日志）
转换按钮图标随当前模式实时切换。
"""

from pathlib import Path

from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QButtonGroup,
    QSizePolicy,
)
from qfluentwidgets import (
    MSFluentWindow,
    CardWidget,
    PushButton,
    PrimaryPushButton,
    LineEdit,
    ProgressBar,
    RadioButton,
    PlainTextEdit,
    SubtitleLabel,
    BodyLabel,
    IconWidget,
    InfoBar,
    InfoBarPosition,
    FluentIcon as FIF,
)

from ..core.config import ConfigManager
from ..core.converter import Converter
from ..core.logger import logger, add_sink, remove_sink


class _Signals(QObject):
    log_arrived = Signal(str)
    progress_updated = Signal(int)
    convert_finished = Signal(object)


class MainWindow(MSFluentWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("CSV 转码 / 转表格工具")
        self.resize(920, 640)
        self.setMinimumSize(760, 520)

        self.config = ConfigManager()
        self.converter = Converter(self.config)
        self.signals = _Signals()

        self._source_path: Path | None = None
        self._mode = "gbk"

        self._build_ui()
        self._connect_signals()
        self._restore_output_dir()
        self._update_convert_icon()

        add_sink(self._on_log_sink)
        logger.info("应用已就绪")

    def _build_ui(self) -> None:
        page = QWidget()
        page.setObjectName("convert_page")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(5)

        layout.addWidget(self._build_input_card())
        layout.addWidget(self._build_option_card())
        layout.addWidget(self._build_log_card(), 1)

        self.addSubInterface(page, FIF.SYNC, "转换")

    def _make_card_title(self, icon, text: str) -> QWidget:
        row = QHBoxLayout()
        row.setSpacing(10)
        row.setContentsMargins(0, 0, 0, 0)
        iw = IconWidget(icon)
        iw.setFixedSize(18, 18)
        title = SubtitleLabel(text)
        row.addWidget(iw)
        row.addWidget(title)
        row.addStretch(1)
        wrap = QWidget()
        wrap.setLayout(row)
        return wrap

    def _build_input_card(self) -> CardWidget:
        card = CardWidget()
        v = QVBoxLayout(card)
        v.setContentsMargins(20, 18, 20, 18)
        v.setSpacing(12)

        v.addWidget(self._make_card_title(FIF.DOCUMENT, "源文件"))

        h = QHBoxLayout()
        h.setSpacing(10)
        label = BodyLabel("CSV 文件：")
        self.path_edit = LineEdit()
        self.path_edit.setPlaceholderText("请选择或输入 CSV 文件路径")
        self.path_edit.setClearButtonEnabled(True)
        self.browse_btn = PushButton(FIF.FOLDER, "浏览")
        self.convert_btn = PrimaryPushButton(FIF.PLAY_SOLID, "转换")
        self.convert_btn.setMinimumWidth(96)

        h.addWidget(label)
        h.addWidget(self.path_edit, 1)
        h.addWidget(self.browse_btn)
        h.addWidget(self.convert_btn)
        v.addLayout(h)
        return card

    def _build_option_card(self) -> CardWidget:
        card = CardWidget()
        v = QVBoxLayout(card)
        v.setContentsMargins(20, 18, 20, 18)
        v.setSpacing(12)

        v.addWidget(self._make_card_title(FIF.SETTING, "转换选项"))

        row = QHBoxLayout()
        row.setSpacing(20)
        self.radio_gbk = RadioButton("转码 (UTF8 → GBK)")
        self.radio_excel = RadioButton("转表格 (CSV → XLSX)")
        self.radio_gbk.setChecked(True)
        self.group = QButtonGroup(self)
        self.group.addButton(self.radio_gbk, 0)
        self.group.addButton(self.radio_excel, 1)

        self.icon_gbk = IconWidget(FIF.LANGUAGE)
        self.icon_gbk.setFixedSize(18, 18)
        self.icon_excel = IconWidget(FIF.SAVE_AS)
        self.icon_excel.setFixedSize(18, 18)

        row.addWidget(self.icon_gbk)
        row.addWidget(self.radio_gbk)
        row.addSpacing(12)
        row.addWidget(self.icon_excel)
        row.addWidget(self.radio_excel)
        row.addStretch(1)

        self.progress_bar = ProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(6)

        out_row = QHBoxLayout()
        out_row.setSpacing(10)
        out_label = BodyLabel("输出目录：")
        self.output_edit = LineEdit()
        self.output_edit.setPlaceholderText("留空则保存到源文件同目录")
        self.output_edit.setClearButtonEnabled(True)
        self.output_browse_btn = PushButton(FIF.FOLDER, "选择")
        out_row.addWidget(out_label)
        out_row.addWidget(self.output_edit, 1)
        out_row.addWidget(self.output_browse_btn)

        v.addLayout(row)
        v.addWidget(self.progress_bar)
        v.addLayout(out_row)
        return card

    def _build_log_card(self) -> CardWidget:
        card = CardWidget()
        v = QVBoxLayout(card)
        v.setContentsMargins(20, 18, 20, 18)
        v.setSpacing(5)

        v.addWidget(self._make_card_title(FIF.MESSAGE, "处理日志"))

        self.log_view = PlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setPlaceholderText("处理日志将显示在此处...")
        self.log_view.setMaximumBlockCount(2000)
        self.log_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        mono = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        mono.setPointSize(10)
        self.log_view.setFont(mono)

        v.addWidget(self.log_view, 1)
        return card

    def _connect_signals(self) -> None:
        self.browse_btn.clicked.connect(self._on_browse)
        self.output_browse_btn.clicked.connect(self._on_output_browse)
        self.convert_btn.clicked.connect(self._on_convert)
        self.path_edit.textChanged.connect(self._on_path_changed)
        self.output_edit.textChanged.connect(self._on_output_dir_changed)
        self.group.idClicked.connect(self._on_mode_changed)

        self.signals.log_arrived.connect(self._append_log)
        self.signals.progress_updated.connect(self._set_progress)
        self.signals.convert_finished.connect(self._on_convert_done)

    def _restore_output_dir(self) -> None:
        if self.config.config.output_dir:
            self.output_edit.setText(str(Path(self.config.config.output_dir)))

    def _update_convert_icon(self) -> None:
        icon = FIF.LANGUAGE if self._mode == "gbk" else FIF.SAVE_AS
        self.convert_btn.setIcon(icon)

    def _on_log_sink(self, line: str) -> None:
        self.signals.log_arrived.emit(line)

    def _append_log(self, line: str) -> None:
        self.log_view.appendPlainText(line)

    def _set_progress(self, value: int) -> None:
        self.progress_bar.setValue(value)

    def _on_browse(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "选择 CSV 文件", "", "CSV 文件 (*.csv);;所有文件 (*)"
        )
        if path:
            self.path_edit.setText(str(Path(path)))

    def _on_output_browse(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if path:
            self.output_edit.setText(str(Path(path)))

    def _on_path_changed(self, text: str) -> None:
        self._source_path = Path(text) if text.strip() else None

    def _on_output_dir_changed(self, text: str) -> None:
        self.config.set_output_dir(text.strip())

    def _on_mode_changed(self, idx: int) -> None:
        self._mode = "gbk" if idx == 0 else "excel"
        self._update_convert_icon()

    def _on_convert(self) -> None:
        if self.converter.is_running:
            return
        if self._source_path is None or not self._source_path.exists():
            InfoBar.warning(
                title="提示",
                content="请先选择有效的 CSV 文件",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2500,
                parent=self,
            )
            return
        if not self._source_path.suffix.lower() == ".csv":
            InfoBar.warning(
                title="提示",
                content="请选择 .csv 文件",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2500,
                parent=self,
            )
            return

        self.convert_btn.setEnabled(False)
        self.browse_btn.setEnabled(False)
        self.convert_btn.setIcon(FIF.SYNC)
        self.progress_bar.setValue(0)
        logger.info("已启动转换任务（模式: {}）", self._mode)

        self.converter.start(
            self._source_path,
            self._mode,
            on_progress=self.signals.progress_updated.emit,
            on_done=self.signals.convert_finished.emit,
        )

    def _on_convert_done(self, result: object) -> None:
        self.convert_btn.setEnabled(True)
        self.browse_btn.setEnabled(True)
        self._update_convert_icon()
        if result is not None:
            InfoBar.success(
                title="完成",
                content=f"已生成: {Path(result).name}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self,
            )
        else:
            InfoBar.error(
                title="失败",
                content="转换失败，请查看日志",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self,
            )

    def closeEvent(self, event) -> None:
        try:
            remove_sink(self._on_log_sink)
        except Exception:
            pass
        super().closeEvent(event)


__all__ = ["MainWindow"]
