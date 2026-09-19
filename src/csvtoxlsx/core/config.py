#!/usr/bin/env python3
# encoding=utf-8
'''
Author: Dodotry
Date: 2026-09-19 21:13:52
LastEditors: Dodotry
LastEditTime: 2026-09-19 22:12:29
'''
"""配置模块。

管理输出目录等运行期配置，使用 TOML 文件持久化。
配置文件默认存放在用户配置目录下：~/.csvtoxlsx/config.toml
"""
import os
from dataclasses import dataclass, asdict
from pathlib import Path

try:
    import tomllib as _toml
    _TOML_LOAD = _toml.loads
except ModuleNotFoundError:
    import tomli as _toml
    _TOML_LOAD = _toml.loads


def _default_config_dir() -> Path:
    home = Path.home()
    return home / ".csvtoxlsx"


@dataclass
class AppConfig:
    output_dir: str = ""
    remember_output_dir: bool = True

    @property
    def resolved_output_dir(self) -> Path | None:
        if self.output_dir and self.output_dir.strip():
            return Path(self.output_dir)
        return None


class ConfigManager:
    def __init__(self, config_dir: Path | None = None) -> None:
        self.config_dir = config_dir or _default_config_dir()
        self.config_file = self.config_dir / "config.toml"
        self.config: AppConfig = AppConfig()
        self.load()

    def load(self) -> AppConfig:
        if not self.config_file.exists():
            return self.config
        try:
            text = self.config_file.read_text(encoding="utf-8")
            data = _TOML_LOAD(text)
            section = data.get("app", {})
            self.config = AppConfig(
                output_dir=section.get("output_dir", ""),
                remember_output_dir=section.get("remember_output_dir", True),
            )
        except Exception:
            self.config = AppConfig()
        return self.config

    def save(self) -> None:
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            cfg = asdict(self.config)
            lines = ["[app]"]
            for k, v in cfg.items():
                if isinstance(v, bool):
                    lines.append(f"{k} = {'true' if v else 'false'}")
                elif isinstance(v, str):
                    escaped = v.replace("\\", "\\\\").replace('"', '\\"')
                    lines.append(f'{k} = "{escaped}"')
                else:
                    lines.append(f"{k} = {v}")
            self.config_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        except Exception:
            pass

    def set_output_dir(self, path: str) -> None:
        self.config.output_dir = path
        if self.config.remember_output_dir:
            self.save()

    def resolve_output_path(self, source_file: Path, suffix: str, new_ext: str) -> Path:
        stem = source_file.stem + suffix
        target_name = f"{stem}.{new_ext}"
        out_dir = self.config.resolved_output_dir
        if out_dir is None:
            return source_file.parent / target_name
        return out_dir / target_name


__all__ = ["AppConfig", "ConfigManager"]