import tkinter as tk
from tkinter import Listbox, Scrollbar, messagebox, Frame
import os
import json

# CapCut 草稿的基础路径 (固定)
BASE_DRAFT_PATH = "/Users/xulong/Movies/CapCut/User Data/Projects/com.lveditor.draft/"


def select_draft_folder_gui():
    """
    弹出一个GUI窗口，让用户从 BASE_DRAFT_PATH 选择一个草稿文件夹。
    返回选中的草稿文件夹的完整路径，如果取消则返回 None。
    """
    if not os.path.isdir(BASE_DRAFT_PATH):
        messagebox.showerror("路径错误", f"CapCut 草稿基础路径不存在或不是一个文件夹:\n{BASE_DRAFT_PATH}")
        return None

    try:
        draft_folders = [d for d in os.listdir(BASE_DRAFT_PATH) if os.path.isdir(os.path.join(BASE_DRAFT_PATH, d))]
        # 按修改时间降序排序文件夹，使得最近的草稿更容易被找到
        # 注意：os.path.getmtime 在某些系统上可能不反映文件夹内容的最新修改，
        # 如果草稿文件夹名本身包含日期，按名称排序可能更直观。这里我们先简单按名称倒序。
        draft_folders.sort(reverse=True)
    except OSError as e:
        messagebox.showerror("读取错误", f"无法读取草稿文件夹列表:\n{BASE_DRAFT_PATH}\n错误: {e}")
        return None

    if not draft_folders:
        messagebox.showinfo("无草稿", f"在路径下未找到任何草稿文件夹:\n{BASE_DRAFT_PATH}")
        return None

    selected_draft_name = None

    window = tk.Tk()
    window.title("选择 CapCut 草稿项目")

    # 设置窗口大小和位置
    window_width = 380
    window_height = 450
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    center_x = int(screen_width / 2 - window_width / 2)
    center_y = int(screen_height / 2 - window_height / 2)
    window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    window.resizable(False, False)

    tk.Label(window, text="请选择一个草稿文件夹:", font=("Arial", 14)).pack(pady=(15, 5))

    listbox_frame = Frame(window)
    listbox_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

    scrollbar = Scrollbar(listbox_frame, orient=tk.VERTICAL)
    listbox = Listbox(listbox_frame, yscrollcommand=scrollbar.set, exportselection=False, font=("Arial", 12), height=15)

    scrollbar.config(command=listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    for folder in draft_folders:
        listbox.insert(tk.END, folder)

    def on_select():
        nonlocal selected_draft_name
        try:
            selected_indices = listbox.curselection()
            if selected_indices:
                selected_draft_name = listbox.get(selected_indices[0])
                window.destroy()
            else:
                messagebox.showwarning("未选择", "请从列表中选择一个草稿文件夹。")
        except tk.TclError:  # 窗口被意外关闭
            selected_draft_name = None
            window.destroy()

    def on_cancel():
        nonlocal selected_draft_name
        selected_draft_name = None
        window.destroy()

    button_frame = Frame(window)
    button_frame.pack(pady=(5, 15))

    ok_button = tk.Button(button_frame, text="确定", command=on_select, width=10, font=("Arial", 12))
    ok_button.pack(side=tk.LEFT, padx=10)

    cancel_button = tk.Button(button_frame, text="取消", command=on_cancel, width=10, font=("Arial", 12))
    cancel_button.pack(side=tk.LEFT, padx=10)

    window.protocol("WM_DELETE_WINDOW", on_cancel)  # 处理窗口关闭按钮
    window.mainloop()

    if selected_draft_name:
        return os.path.join(BASE_DRAFT_PATH, selected_draft_name)
    return None


def format_time_srt(microseconds):
    """将微秒时间格式化为 SRT 的 HH:MM:SS,ms 格式"""
    if not isinstance(microseconds, (int, float)) or microseconds < 0:
        microseconds = 0

    total_milliseconds = int(microseconds // 1000)  # 转换为毫秒并取整

    hours = total_milliseconds // 3600000
    total_milliseconds %= 3600000

    minutes = total_milliseconds // 60000
    total_milliseconds %= 60000

    seconds = total_milliseconds // 1000
    milliseconds = total_milliseconds % 1000

    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


def extract_subtitles(draft_project_path):
    """
    从指定的 CapCut 草稿项目路径中提取字幕数据。
    返回 SRT 格式的字符串，如果失败或无字幕则返回 None 或空字符串。
    """
    draft_info_file_path = os.path.join(draft_project_path, "draft_info.json")

    if not os.path.exists(draft_info_file_path):
        messagebox.showerror("文件未找到", f"draft_info.json 文件不存在于:\n{draft_info_file_path}")
        return None

    try:
        with open(draft_info_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        messagebox.showerror("JSON错误", f"解析 draft_info.json 文件失败。\n文件可能已损坏或格式不正确。")
        return None
    except Exception as e:
        messagebox.showerror("读取错误", f"读取 draft_info.json 文件时发生未知错误:\n{e}")
        return None

    subtitles_data = []

    materials = data.get('materials')
    if not materials or not isinstance(materials.get('texts'), list):
        # messagebox.showinfo("无字幕信息", "在 draft_info.json 中未找到有效的 'materials.texts' 数据。")
        # 允许继续，可能字幕在其他结构，但根据用户提供的文件，这里是关键
        all_texts_items = []
    else:
        all_texts_items = materials.get('texts', [])

    tracks = data.get('tracks')
    if not isinstance(tracks, list):
        # messagebox.showinfo("无轨道信息", "在 draft_info.json 中未找到有效的 'tracks' 数据。")
        # 允许继续，但可能无法找到时间
        all_tracks_items = []
    else:
        all_tracks_items = tracks

    for text_item in all_texts_items:
        if not isinstance(text_item, dict):
            continue

        text_id = text_item.get('id')
        if not text_id:
            continue

        # 提取文本内容
        current_text = text_item.get('recognize_text', '').strip()  # 优先使用 recognize_text
        if not current_text:  # 如果 recognize_text 为空，尝试解析 content 字段
            content_str = text_item.get('content')
            if content_str:
                try:
                    content_data = json.loads(content_str)
                    current_text = content_data.get('text', '').strip()
                except (json.JSONDecodeError, TypeError):
                    # 如果 content 不是有效的 JSON 字符串或解析失败，则 current_text 保持为空
                    pass

        if not current_text:  # 如果最终文本内容为空，则跳过
            continue

        # 在轨道中查找此文本的时间信息
        for track in all_tracks_items:
            if not isinstance(track, dict) or track.get('type') != 'text':
                continue

            segments = track.get('segments', [])
            if not isinstance(segments, list):
                continue

            for segment in segments:
                if not isinstance(segment, dict) or segment.get('material_id') != text_id:
                    continue

                target_timerange = segment.get('target_timerange')
                if isinstance(target_timerange, dict):
                    start_us = target_timerange.get('start')
                    duration_us = target_timerange.get('duration')

                    if isinstance(start_us, (int, float)) and isinstance(duration_us, (int, float)) and duration_us > 0:
                        end_us = start_us + duration_us
                        subtitles_data.append({
                            'start_us': start_us,
                            'end_us': end_us,
                            'text': current_text
                        })
                        # 假设一个 text_id 在时间轴上只出现一次（或我们只取第一次匹配到的）
                        # 如果一个文本素材被多次使用，这里可能需要调整
                        break
            else:  # 内层循环正常结束 (没 break)
                continue  # 继续到下一个轨道
            break  # 内层循环 break 了 (找到了 segment)，外层循环也 break (找到了 track)

    if not subtitles_data:
        messagebox.showinfo("无字幕", "未能从项目中提取到任何字幕内容。")
        return ""  # 返回空字符串表示没有字幕

    # 按开始时间排序
    subtitles_data.sort(key=lambda x: x['start_us'])

    # 构建SRT内容
    srt_output_lines = []
    for i, sub_info in enumerate(subtitles_data, 1):
        srt_start = format_time_srt(sub_info['start_us'])
        srt_end = format_time_srt(sub_info['end_us'])

        srt_output_lines.append(str(i))
        srt_output_lines.append(f"{srt_start} --> {srt_end}")
        srt_output_lines.append(sub_info['text'])
        srt_output_lines.append("")  # SRT 条目间的空行

    return "\n".join(srt_output_lines)


def main():
    # 1. 让用户选择草稿文件夹
    selected_project_path = select_draft_folder_gui()

    if not selected_project_path:
        # print("用户取消选择或未选择文件夹。")
        return

    # 2. 从选择的草稿中提取字幕
    srt_content = extract_subtitles(selected_project_path)

    if srt_content is None:  # 表示提取过程中发生错误
        # print("提取字幕时发生错误。")
        return

    if not srt_content.strip():  # 表示没有字幕内容被提取
        # print("没有字幕内容可供保存。")
        return

    # 3. 确定输出文件名和路径
    draft_folder_name = os.path.basename(selected_project_path)
    srt_filename = f"{draft_folder_name}_subtitles.srt"

    # 获取脚本所在的目录
    try:
        # __file__ 在作为脚本运行时是定义的
        script_directory = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        # 如果在交互式环境（如IDLE）中运行，__file__ 可能未定义，则使用当前工作目录
        script_directory = os.getcwd()

    output_srt_path = os.path.join(script_directory, srt_filename)

    # 4. 保存 SRT 文件
    try:
        with open(output_srt_path, 'w', encoding='utf-8') as f:
            f.write(srt_content)
        messagebox.showinfo("导出成功", f"字幕文件已成功保存到:\n{output_srt_path}")
    except IOError as e:
        messagebox.showerror("保存失败", f"无法写入SRT文件到:\n{output_srt_path}\n错误: {e}")
    except Exception as e:
        messagebox.showerror("未知保存错误", f"保存SRT文件时发生未知错误:\n{e}")


if __name__ == "__main__":
    main()