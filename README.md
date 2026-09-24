# csvtoxlsx

CSV 转 GBK 编码或转 Excel 文件工具，带 Fluent 风格图形界面。

## 功能

- **转码**：将 CSV 文件转换为 GBK 编码的 CSV（解决旧系统/软件读取中文乱码问题）
- **转表格**：将 CSV 文件转换为 Excel（`.xlsx`）文件
- 实时进度条与处理日志显示
- 输出目录可配置，默认保存到源文件同目录
- 转换在后台线程执行，界面不卡顿

## 技术栈

| 组件 | 说明 |
| --- | --- |
| Python 3.14 | 运行时 |
| [PySide6-Fluent-Widgets](https://github.com/zhiyiYo/PySide6-Fluent-Widgets) | Fluent 设计风格 UI |
| [loguru](https://github.com/Delgan/loguru) | 日志库 |
| [polars](https://github.com/pola-rs/polars) | CSV 读取与数据处理 |
| xlsxwriter | Excel 写入后端（polars `write_excel` 依赖） |
| uv | 包管理与虚拟环境 |

## 安装

```bash
uv sync
```

## 运行

```bash
uv run csvtoxlsx
```

或直接通过模块入口：

```bash
uv run python -u -m csvtoxlsx.main
```

## 使用说明

1. 点击 **浏览** 选择 CSV 源文件，或在地址栏直接输入路径
2. 在 **转换选项** 中选择模式：
   - **转码 (CSV → GBK)**：生成 `<原名>_GBK.csv`
   - **转表格 (CSV → XLSX)**：生成 `<原名>.xlsx`
3. （可选）设置 **输出目录**，留空则保存到源文件同目录
4. 点击 **转换**，进度条与下方日志区实时显示处理过程；转换期间按钮自动禁用

## 配置

输出目录等配置持久化在用户主目录下：

```
~/.csvtoxlsx/config.toml
```

示例：

```toml
[app]
output_dir = "D:\\output"
remember_output_dir = true
```

## 项目结构

```
src/csvtoxlsx/
├── __init__.py          # 包入口
├── main.py              # 应用启动：QApplication、主题色、本地化翻译
├── core/
│   ├── logger.py        # loguru 日志，支持 sink 回调推送至界面
│   ├── config.py        # TOML 配置管理（输出目录持久化）
│   └── converter.py     # 转换逻辑：CSV→GBK、CSV→XLSX，子线程执行
└── ui/
    └── main_window.py   # Fluent 主窗口与交互
```

界面（`ui/`）与转换逻辑（`core/`）严格分离，通过 `Signal` 跨线程通信。

## 界面主题

- 主题色：微软蓝 `#0078D4`
- 图标随当前模式实时切换：转码 → `LANGUAGE`，转表格 → `SAVE_AS`，运行中 → `SYNC`
- 根据系统 locale 自动加载 Qt 翻译文件，右键菜单等内置控件跟随系统语言

## 依赖说明

- `xlsxwriter`：polars 的 `write_excel` 需要，用于生成 `.xlsx`
- `openpyxl`：用于读取/校验生成的 `.xlsx` 文件




```powershell

FROM ./Bonsai-27B-Q1_0.gguf
PARAMETER num_ctx 65536
PARAMETER num_gpu 99


ollama create bonsai27b -f Modelfile
ollama run bonsai27b


```