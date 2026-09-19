#!/usr/bin/env python3
# encoding=utf-8
'''
Author: Dodotry
Date: 2026-09-19 21:13:22
LastEditors: Dodotry
LastEditTime: 2026-09-19 22:13:51
'''
"""日志模块。

基于 loguru，提供应用级单例 logger，并支持把日志消息通过回调实时推送到界面信息框。
"""
import sys
from typing import Callable

from loguru import logger as _logger

LoggerSink = Callable[[str], None]

_sink_callbacks: list[LoggerSink] = []


def _intercept_sink(message) -> None:
    record = message.record
    level = record["level"].name
    text = str(record["message"])
    line = f"{level.upper()} | {text}"
    for cb in _sink_callbacks:
        try:
            cb(line)
        except Exception:
            pass


def setup_logger() -> None:
    _logger.remove()
    _logger.add(
        sys.stderr,
        level="DEBUG",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
        colorize=True,
    )
    _logger.add(_intercept_sink, level="INFO", format="{message}")


def add_sink(callback: LoggerSink) -> None:
    if callback not in _sink_callbacks:
        _sink_callbacks.append(callback)


def remove_sink(callback: LoggerSink) -> None:
    if callback in _sink_callbacks:
        _sink_callbacks.remove(callback)


logger = _logger

__all__ = ["logger", "setup_logger", "add_sink", "remove_sink"]