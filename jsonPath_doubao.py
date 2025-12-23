import json
import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk
import re


class JSONPathFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("JSON节点路径查询工具")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # 设置样式
        self.style = ttk.Style()
        self.style.configure("TButton", font=("微软雅黑", 10))
        self.style.configure("TLabel", font=("微软雅黑", 10))
        self.style.configure("TEntry", font=("微软雅黑", 10))

        # 创建界面组件
        self.create_widgets()

    def create_widgets(self):
        # 顶部文件选择区域
        file_frame = ttk.Frame(self.root, padding="10")
        file_frame.pack(fill=tk.X)

        ttk.Label(file_frame, text="JSON文件:").pack(side=tk.LEFT, padx=5)
        
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=50)
        file_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        browse_btn = ttk.Button(file_frame, text="浏览", command=self.browse_file)
        browse_btn.pack(side=tk.LEFT, padx=5)

        # 节点输入区域
        node_frame = ttk.Frame(self.root, padding="10")
        node_frame.pack(fill=tk.X)

        ttk.Label(node_frame, text="目标节点(逗号分隔):").pack(side=tk.LEFT, padx=5)
        
        self.node_entry = ttk.Entry(node_frame, width=50)
        self.node_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.node_entry.insert(0, "event_name,msgId,triggerType,timestamp")  # 默认值

        # 操作按钮区域
        btn_frame = ttk.Frame(self.root, padding="10")
        btn_frame.pack(fill=tk.X)

        self.run_btn = ttk.Button(btn_frame, text="查询节点路径", command=self.run_search)
        self.run_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(btn_frame, text="清空结果", command=self.clear_results)
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        # 结果展示区域
        result_frame = ttk.Frame(self.root, padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(result_frame, text="查询结果:").pack(anchor=tk.W)
        
        self.result_text = scrolledtext.ScrolledText(
            result_frame, 
            wrap=tk.WORD, 
            font=("微软雅黑", 10)
        )
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=5)
        self.result_text.config(state=tk.DISABLED)

    def browse_file(self):
        """选择JSON文件"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)

    def find_key_paths(self, data, target_keys, current_path="", results=None):
        """查找目标节点的路径"""
        if results is None:
            results = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                # 拼接当前路径
                new_path = f"{current_path}/{key}" if current_path else key
                
                # 如果当前 key 在目标列表中
                if key in target_keys:
                    results.append(f"{new_path} = {value}")
                    
                # 递归处理子节点
                self.find_key_paths(value, target_keys, new_path, results)
                
        elif isinstance(data, list):
            for index, item in enumerate(data):
                # 处理数组时添加索引
                new_path = f"{current_path}[{index}]" if current_path else f"[{index}]"
                self.find_key_paths(item, target_keys, new_path, results)
        
        return results

    def run_search(self):
        """执行查询操作"""
        # 清空之前的结果
        self.clear_results()
        
        # 获取文件路径
        file_path = self.file_path_var.get()
        if not file_path:
            self.show_message("请先选择JSON文件")
            return
        
        # 获取目标节点
        node_text = self.node_entry.get().strip()
        if not node_text:
            self.show_message("请输入目标节点")
            return
        
        # 解析目标节点列表（支持逗号分隔，自动忽略空格）
        target_keys = [key.strip() for key in re.split(r',+', node_text) if key.strip()]
        
        try:
            # 读取并解析JSON文件
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            
            # 查找节点路径
            results = self.find_key_paths(data, target_keys)
            
            # 显示结果
            self.result_text.config(state=tk.NORMAL)
            if results:
                self.result_text.insert(tk.END, f"找到 {len(results)} 个匹配结果：\n\n")
                for i, item in enumerate(results, 1):
                    self.result_text.insert(tk.END, f"{i}. {item}\n")
            else:
                self.result_text.insert(tk.END, "未找到匹配的节点")
            self.result_text.config(state=tk.DISABLED)
            
        except Exception as e:
            self.show_message(f"发生错误：{str(e)}")

    def show_message(self, message):
        """显示提示信息"""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, message)
        self.result_text.config(state=tk.DISABLED)

    def clear_results(self):
        """清空结果区域"""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = JSONPathFinder(root)
    root.mainloop()