"""
批量文件整理工具（纯tkinter版，无额外依赖）
"""
from collections import defaultdict
from pathlib import Path
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class 文件整理工具:
    def __init__(self, root):
        self.root = root
        self.root.title("批量文件整理工具")
        self.root.geometry("500x300")
        
        self.目标文件夹 = tk.StringVar()
        self.文件名前缀 = tk.StringVar(value="设计文件")
        self.跳过隐藏文件 = tk.BooleanVar(value=False)
        self.跳过本脚本 = tk.BooleanVar(value=False)
        
        self.创建界面()

    def 创建界面(self):
        # 文件夹选择
        ttk.Label(self.root, text="目标文件夹：").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        ttk.Entry(self.root, textvariable=self.目标文件夹, width=40).grid(row=0, column=1, padx=10, pady=10)
        ttk.Button(self.root, text="选择文件夹", command=self.选择文件夹).grid(row=0, column=2, padx=10, pady=10)
        
        # 文件名前缀
        ttk.Label(self.root, text="文件名前缀：").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        ttk.Entry(self.root, textvariable=self.文件名前缀, width=40).grid(row=1, column=1, padx=10, pady=10)
        
        # 选项
        ttk.Checkbutton(self.root, text="跳过隐藏文件", variable=self.跳过隐藏文件).grid(row=2, column=1, padx=10, pady=5, sticky="w")
        ttk.Checkbutton(self.root, text="跳过本脚本", variable=self.跳过本脚本).grid(row=3, column=1, padx=10, pady=5, sticky="w")
        
        # 按钮
        ttk.Button(self.root, text="开始整理", command=self.开始整理).grid(row=4, column=1, padx=10, pady=20)
        
        # 状态
        self.状态标签 = ttk.Label(self.root, text="准备就绪")
        self.状态标签.grid(row=5, column=1, padx=10, pady=10)

    def 选择文件夹(self):
        文件夹路径 = filedialog.askdirectory()
        if 文件夹路径:
            self.目标文件夹.set(文件夹路径)

    def 开始整理(self):
        目标文件夹 = Path(self.目标文件夹.get()).expanduser().resolve()
        文件名前缀 = self.文件名前缀.get()
        跳过隐藏文件 = self.跳过隐藏文件.get()
        跳过本脚本 = self.跳过本脚本.get()
        
        if not 目标文件夹.is_dir():
            messagebox.showerror("错误", "请先选择有效的文件夹！")
            return
        
        所有路径 = []
        for 项 in 目标文件夹.iterdir():
            if not 项.is_file():
                continue
            if 跳过隐藏文件 and 项.name.startswith("."):
                continue
            if 跳过本脚本 and 项.resolve() == Path(__file__).resolve():
                continue
            所有路径.append(项)

        if not 所有路径:
            messagebox.showinfo("提示", "该文件夹里没有可整理的文件。")
            self.状态标签.config(text="准备就绪")
            return

        # 按扩展名分组
        按扩展名分组 = defaultdict(list)
        for 路径 in 所有路径:
            分组键 = 路径.suffix.lower()
            按扩展名分组[分组键].append(路径)
        for 键 in 按扩展名分组:
            按扩展名分组[键].sort(key=lambda p: p.name.lower())

        待重命名 = []
        for 分组键 in sorted(按扩展名分组.keys(), key=lambda k: (k == "", k.lower())):
            for 组内序号, 原路径 in enumerate(按扩展名分组[分组键], start=1):
                待重命名.append((原路径, 原路径.suffix, 组内序号))

        # 临时重命名（防冲突）
        临时列表 = []
        临时前缀 = f".__批量重命名临时_{int(time.time())}_"

        for 全局序号, (原路径, 后缀, 组内序号) in enumerate(待重命名, start=1):
            临时名 = 目标文件夹 / f"{临时前缀}{全局序号}{后缀}"
            原路径.rename(临时名)
            临时列表.append((临时名, 后缀, 组内序号))

        # 最终重命名
        for 临时路径, 后缀, 组内序号 in 临时列表:
            新名字 = f"{文件名前缀}{组内序号}{后缀}"
            新路径 = 目标文件夹 / 新名字
            if 新路径.exists() and 新路径 != 临时路径:
                print("【错误】目标文件名已存在：", 新名字)
                return
            临时路径.rename(新路径)

        messagebox.showinfo("完成", f"共重命名 {len(临时列表)} 个文件！")
        self.状态标签.config(text="整理完成！")

if __name__ == "__main__":
    root = tk.Tk()
    app = 文件整理工具(root)
    root.mainloop()