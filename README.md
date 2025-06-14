# CapCut字幕srt提取工具 (CapCut Subtitle Extractor)

这是一个 Python 脚本工具，用于从 macOS 版 CapCut（剪映国际版）的桌面应用项目文件中提取字幕，并将其导出为标准的 `.srt` 字幕文件。
由于 CapCut 官方导出字幕功能可能需要付费或存在不便，本工具提供了一个免费的替代方案。

## 功能特性

*   **图形用户界面 (GUI)**：通过简单的弹窗界面，用户可以方便地选择要处理的 CapCut 草稿项目。
*   **自动定位草稿**：脚本预设了 macOS CapCut 的默认草稿项目路径。
*   **智能文本提取**：
    *   优先提取 CapCut 自动识别的字幕文本 (`recognize_text`)。
    *   如果自动识别文本为空，则尝试从手动编辑的文本内容 (`content` 字段中的 JSON 结构) 中提取。
*   **精确时间码**：从项目文件中读取精确的开始时间和结束时间（微秒级），并转换为标准的 SRT 时间码格式 (`HH:MM:SS,ms`)。
*   **自动排序**：导出的字幕条目会根据其在视频中的出现时间自动排序。
*   **忽略空字幕**：文本内容为空或仅包含空格的字幕条目将被自动忽略，保持 SRT 文件整洁。
*   **跨平台兼容性 (核心逻辑)**：虽然 GUI 和默认路径针对 macOS，但核心的 JSON 解析和 SRT 生成逻辑是跨平台的。

## 环境要求

*   **操作系统**：主要为 macOS 开发和测试。
    *   Windows/Linux 用户：核心逻辑可能有效，但需要手动修改 `BASE_DRAFT_PATH` 常量，并且 `tkinter` GUI 在不同系统上的表现可能略有差异。
*   **Python 版本**：Python 3.6 或更高版本。
*   **依赖库**：
    *   `tkinter`：用于图形用户界面。这通常是 Python 标准库的一部分，无需额外安装。
    *   `json`, `os`：Python 标准库。

## 使用方法

1.  **下载脚本**：
    *   将 `capcut_srt_extractor.py` 文件下载到你的电脑任意位置。

2.  **运行脚本**：
    *   **通过 PyCharm (或其他 IDE)**:
        1.  在 PyCharm 中打开 `capcut_srt_extractor.py` 文件。
        2.  直接运行该 Python 文件。
    *   **通过终端 (Terminal)**:
        1.  打开终端应用程序。
        2.  使用 `cd` 命令切换到脚本所在的目录，例如：
            ```bash
            cd /path/to/your/scripts
            ```
        3.  运行脚本：
            ```bash
            python capcut_srt_extractor.py
            ```

3.  **选择 CapCut 草稿项目**：
    *   脚本运行后，会弹出一个标题为“选择 CapCut 草稿项目”的窗口。
    *   此窗口会列出在默认路径 `/Users/YOUR_USERNAME/Movies/CapCut/User Data/Projects/com.lveditor.draft/` 下找到的所有草稿文件夹。
        *   **注意**：请确保你的 CapCut 草稿项目确实存放在此路径下。如果不是，你需要修改脚本文件中的 `BASE_DRAFT_PATH` 常量为你实际的草稿根路径。
    *   从列表中选择你想要提取字幕的草稿项目文件夹（通常以日期或自定义名称命名，如 `0614`）。
    *   点击“确定”按钮。

4.  **字幕提取与保存**：
    *   脚本会自动解析所选草稿项目中的 `draft_info.json` 文件。
    *   提取到的字幕内容将被格式化为 `.srt` 文件。
    *   生成的 `.srt` 文件会自动保存在 **运行该 Python 脚本的相同目录下**。
    *   文件名将基于你选择的草稿文件夹名，例如，如果你选择了名为 `0614` 的草稿，生成的 SRT 文件将是 `0614_subtitles.srt`。
    *   操作完成后，会弹出提示框告知成功或失败，并显示 SRT 文件的保存路径。

## 文件结构与关键逻辑

CapCut 的项目信息主要存储在草稿文件夹内的 `draft_info.json` 文件中。本工具主要解析以下关键部分：

*   `materials.texts`: 存储所有文本素材的原始信息，包括文本ID和内容。
*   `tracks`: 存储时间轴信息。类型为 "text" 的轨道包含了文本片段 (segments)。
    *   每个文本片段通过 `material_id` 关联到 `materials.texts` 中的具体文本。
    *   `target_timerange` 字段定义了该文本片段在时间轴上的开始时间 (`start`) 和持续时间 (`duration`)，单位为微秒。

## 注意事项

*   **CapCut 版本兼容性**：此工具基于特定版本的 CapCut (macOS, `com.lveditor.draft`) 项目文件结构进行开发。如果 CapCut 未来的版本更改了 `draft_info.json` 的结构，此工具可能需要更新。
*   **草稿路径**：如果你的 CapCut 草稿根路径与脚本中预设的 `BASE_DRAFT_PATH` (`/Users/YOUR_USERNAME/Movies/CapCut/User Data/Projects/com.lveditor.draft/`) 不同，请务必在脚本中修改此常量。将 `YOUR_USERNAME` 替换为你的实际 macOS 用户名。
*   **错误处理**：脚本包含基本的错误处理，如路径不存在、JSON 解析失败等，并通过弹窗提示用户。
*   **多文本轨道**：脚本会提取项目中所有标记为“text”类型的轨道上的字幕，并按时间顺序合并到一个 SRT 文件中。
*   **仅限文本字幕**：此工具仅用于提取通过 CapCut 文本功能（包括自动字幕和手动添加的文本框）创建的字幕。它不能提取硬编码到视频中的字幕或图片形式的字幕。

## 贡献

欢迎提交 Issues 和 Pull Requests 来改进此工具。如果你发现了 bug，或者有新的功能建议，请随时提出。

## 免责声明

本工具为开源免费软件，仅供学习和个人使用。请遵守 CapCut 的用户协议。对于使用本工具可能产生的任何直接或间接后果，开发者不承担任何责任。

---
