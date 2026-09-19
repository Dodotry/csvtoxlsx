"""CSV 转换逻辑模块。

提供两种转换：
1. CSV -> GBK 编码的 CSV（保持 csv 格式，编码转为 GBK）
2. CSV -> Excel (.xlsx)

转换在独立线程中执行，通过回调实时上报进度与日志。
"""

import threading
from pathlib import Path
from typing import Callable, Optional

import polars as pl

from .config import ConfigManager
from .logger import logger

ProgressCallback = Callable[[int], None]
DoneCallback = Callable[[Optional[Path]], None]


class ConversionError(Exception):
    pass


class Converter:
    def __init__(self, config: ConfigManager) -> None:
        self.config = config
        self._thread: threading.Thread | None = None

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(
        self,
        source: Path,
        mode: str,
        on_progress: ProgressCallback | None = None,
        on_done: DoneCallback | None = None,
    ) -> None:
        if self.is_running:
            raise ConversionError("已有转换任务正在运行")
        self._thread = threading.Thread(
            target=self._run,
            args=(source, mode, on_progress, on_done),
            daemon=True,
        )
        self._thread.start()

    def _run(
        self,
        source: Path,
        mode: str,
        on_progress: ProgressCallback | None,
        on_done: DoneCallback | None,
    ) -> None:
        result: Path | None = None
        try:
            if mode == "gbk":
                result = self._convert_to_gbk(source, on_progress)
            elif mode == "excel":
                result = self._convert_to_excel(source, on_progress)
            else:
                raise ConversionError(f"未知转换模式: {mode}")
        except Exception as exc:
            logger.exception("转换失败: {}", exc)
            result = None
        finally:
            if on_done is not None:
                on_done(result)

    def _convert_to_gbk(self, source: Path, on_progress: ProgressCallback | None) -> Path:
        logger.info("开始转码: {} -> GBK", source)
        self._report(on_progress, 5)

        if not source.exists():
            raise ConversionError(f"源文件不存在: {source}")

        logger.info("读取 CSV（polars 自动探测编码）...")
        df = pl.read_csv(source, ignore_errors=True, try_parse_dates=True)
        self._report(on_progress, 40)
        logger.info("读取完成，共 {} 行 × {} 列", df.height, df.width)

        target = self.config.resolve_output_path(source, "_GBK", "csv")
        logger.info("目标文件: {}", target)

        csv_text = df.write_csv()
        self._report(on_progress, 70)

        with open(target, "w", encoding="gbk", newline="") as fp:
            fp.write(csv_text)
        self._report(on_progress, 95)

        size_kb = target.stat().st_size / 1024
        logger.info("转码完成: {} ({:.2f} KB)", target.name, size_kb)
        self._report(on_progress, 100)
        return target

    def _convert_to_excel(self, source: Path, on_progress: ProgressCallback | None) -> Path:
        logger.info("开始转表格: {} -> XLSX", source)
        self._report(on_progress, 5)

        if not source.exists():
            raise ConversionError(f"源文件不存在: {source}")

        logger.info("读取 CSV...")
        df = pl.read_csv(source, ignore_errors=True, try_parse_dates=True)
        self._report(on_progress, 40)
        logger.info("读取完成，共 {} 行 × {} 列", df.height, df.width)

        target = self.config.resolve_output_path(source, "", "xlsx")
        logger.info("目标文件: {}", target)

        df.write_excel(target)
        self._report(on_progress, 90)

        size_kb = target.stat().st_size / 1024
        logger.info("转表格完成: {} ({:.2f} KB)", target.name, size_kb)
        self._report(on_progress, 100)
        return target

    @staticmethod
    def _report(cb: ProgressCallback | None, value: int) -> None:
        if cb is not None:
            try:
                cb(value)
            except Exception:
                pass


__all__ = ["Converter", "ConversionError"]