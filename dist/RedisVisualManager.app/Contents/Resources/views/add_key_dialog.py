"""
新增/编辑Key对话框
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict


class AddKeyDialog:
    """新增/编辑Key对话框"""
    
    def __init__(self, parent, redis_model, key: str = None, key_type: str = None):
        self.parent = parent
        self.redis_model = redis_model
        self.key = key
        self.is_edit = key is not None
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("新增Key" if not self.is_edit else f"编辑Key: {key}")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.center_window()
        self.setup_ui()
        
        if self.is_edit:
            self.load_key_data(key_type)
    
    def center_window(self):
        """窗口居中"""
        self.dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() - 600) // 2
        y = self.parent.winfo_y() + (self.parent.winfo_height() - 500) // 2
        self.dialog.geometry(f"600x500+{x}+{y}")
    
    def setup_ui(self):
        """设置界面"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Key名称
        ttk.Label(main_frame, text="Key名称:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.key_var = tk.StringVar(value=self.key if self.key else "")
        self.key_entry = ttk.Entry(main_frame, textvariable=self.key_var, width=40)
        self.key_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        if self.is_edit:
            self.key_entry.config(state='readonly')
        
        # 数据类型
        ttk.Label(main_frame, text="数据类型:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.type_var = tk.StringVar(value="string")
        type_frame = ttk.Frame(main_frame)
        type_frame.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        types = [("string", "string"), ("hash", "hash"), ("list", "list"), 
                 ("set", "set"), ("zset", "zset")]
        for text, val in types:
            rb = ttk.Radiobutton(type_frame, text=text, variable=self.type_var, 
                                value=val, command=self.on_type_change)
            rb.pack(side=tk.LEFT, padx=5)
        
        # 过期时间
        ttk.Label(main_frame, text="过期时间(秒):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.ttl_var = tk.StringVar(value="0")
        self.ttl_entry = ttk.Entry(main_frame, textvariable=self.ttl_var, width=15)
        self.ttl_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        ttk.Label(main_frame, text="(0表示永不过期)").grid(row=2, column=2, sticky=tk.W, pady=5)
        
        # 值编辑区域
        self.value_frame = ttk.LabelFrame(main_frame, text="值", padding="10")
        self.value_frame.grid(row=3, column=0, columnspan=3, sticky="nsew", pady=10)
        main_frame.rowconfigure(3, weight=1)
        
        # String值
        self.string_frame = ttk.Frame(self.value_frame)
        self.string_text = tk.Text(self.string_frame, height=10, width=50)
        self.string_scroll = ttk.Scrollbar(self.string_frame, orient=tk.VERTICAL, 
                                           command=self.string_text.yview)
        self.string_text.configure(yscrollcommand=self.string_scroll.set)
        self.string_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.string_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Hash值
        self.hash_frame = ttk.Frame(self.value_frame)
        ttk.Label(self.hash_frame, text="格式: field=value (每行一个)").pack(anchor=tk.W)
        self.hash_text = tk.Text(self.hash_frame, height=10, width=50)
        self.hash_scroll = ttk.Scrollbar(self.hash_frame, orient=tk.VERTICAL, 
                                         command=self.hash_text.yview)
        self.hash_text.configure(yscrollcommand=self.hash_scroll.set)
        self.hash_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.hash_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # List值
        self.list_frame = ttk.Frame(self.value_frame)
        ttk.Label(self.list_frame, text="格式: 每行一个元素").pack(anchor=tk.W)
        self.list_text = tk.Text(self.list_frame, height=10, width=50)
        self.list_scroll = ttk.Scrollbar(self.list_frame, orient=tk.VERTICAL, 
                                         command=self.list_text.yview)
        self.list_text.configure(yscrollcommand=self.list_scroll.set)
        self.list_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Set值
        self.set_frame = ttk.Frame(self.value_frame)
        ttk.Label(self.set_frame, text="格式: 每行一个成员").pack(anchor=tk.W)
        self.set_text = tk.Text(self.set_frame, height=10, width=50)
        self.set_scroll = ttk.Scrollbar(self.set_frame, orient=tk.VERTICAL, 
                                        command=self.set_text.yview)
        self.set_text.configure(yscrollcommand=self.set_scroll.set)
        self.set_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.set_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # ZSet值
        self.zset_frame = ttk.Frame(self.value_frame)
        ttk.Label(self.zset_frame, text="格式: member=score (每行一个)").pack(anchor=tk.W)
        self.zset_text = tk.Text(self.zset_frame, height=10, width=50)
        self.zset_scroll = ttk.Scrollbar(self.zset_frame, orient=tk.VERTICAL, 
                                         command=self.zset_text.yview)
        self.zset_text.configure(yscrollcommand=self.zset_scroll.set)
        self.zset_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.zset_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 按钮区域
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=4, column=0, columnspan=3, pady=10)
        
        ttk.Button(btn_frame, text="保存", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        self.on_type_change()
    
    def on_type_change(self):
        """类型切换时显示对应的编辑框"""
        # 隐藏所有
        self.string_frame.pack_forget()
        self.hash_frame.pack_forget()
        self.list_frame.pack_forget()
        self.set_frame.pack_forget()
        self.zset_frame.pack_forget()
        
        # 显示对应的
        type_val = self.type_var.get()
        if type_val == 'string':
            self.string_frame.pack(fill=tk.BOTH, expand=True)
        elif type_val == 'hash':
            self.hash_frame.pack(fill=tk.BOTH, expand=True)
        elif type_val == 'list':
            self.list_frame.pack(fill=tk.BOTH, expand=True)
        elif type_val == 'set':
            self.set_frame.pack(fill=tk.BOTH, expand=True)
        elif type_val == 'zset':
            self.zset_frame.pack(fill=tk.BOTH, expand=True)
    
    def load_key_data(self, key_type: str = None):
        """加载已有key的数据"""
        if not key_type:
            key_type = self.redis_model.get_key_type(self.key)
        
        self.type_var.set(key_type)
        self.on_type_change()
        
        # 获取TTL
        ttl = self.redis_model.get_key_ttl(self.key)
        if ttl > 0:
            self.ttl_var.set(str(ttl))
        else:
            self.ttl_var.set("0")
        
        # 获取值
        value = self.redis_model.get_key_value(self.key)
        if value is not None:
            if key_type == 'string':
                self.string_text.insert(tk.END, str(value))
            elif key_type == 'hash':
                for field, val in value.items():
                    self.hash_text.insert(tk.END, f"{field}={val}\n")
            elif key_type == 'list':
                for item in value:
                    self.list_text.insert(tk.END, f"{item}\n")
            elif key_type == 'set':
                for item in value:
                    self.set_text.insert(tk.END, f"{item}\n")
            elif key_type == 'zset':
                for member, score in value:
                    self.zset_text.insert(tk.END, f"{member}={score}\n")
    
    def save(self):
        """保存key"""
        key = self.key_var.get().strip()
        if not key:
            messagebox.showwarning("提示", "Key名称不能为空")
            return
        
        try:
            ttl = int(self.ttl_var.get().strip())
            if ttl < 0:
                messagebox.showwarning("提示", "过期时间不能为负数")
                return
        except ValueError:
            messagebox.showerror("错误", "过期时间必须是数字")
            return
        
        key_type = self.type_var.get()
        
        try:
            if key_type == 'string':
                value = self.string_text.get("1.0", tk.END).strip()
                if self.is_edit:
                    success, msg = self.redis_model.update_string_value(key, value)
                else:
                    success, msg = self.redis_model.add_string_key(key, value, ttl)
            
            elif key_type == 'hash':
                text = self.hash_text.get("1.0", tk.END).strip()
                mapping = {}
                for line in text.split('\n'):
                    if '=' in line:
                        field, val = line.split('=', 1)
                        mapping[field.strip()] = val.strip()
                if not mapping:
                    messagebox.showwarning("提示", "Hash至少需要一个field=value")
                    return
                if self.is_edit:
                    success, msg = self.redis_model.update_hash_value(key, mapping)
                else:
                    success, msg = self.redis_model.add_hash_key(key, mapping, ttl)
            
            elif key_type == 'list':
                text = self.list_text.get("1.0", tk.END).strip()
                values = [v.strip() for v in text.split('\n') if v.strip()]
                if not values:
                    messagebox.showwarning("提示", "List至少需要一个元素")
                    return
                if self.is_edit:
                    success, msg = self.redis_model.update_list_value(key, values)
                else:
                    success, msg = self.redis_model.add_list_key(key, values, ttl)
            
            elif key_type == 'set':
                text = self.set_text.get("1.0", tk.END).strip()
                members = [m.strip() for m in text.split('\n') if m.strip()]
                if not members:
                    messagebox.showwarning("提示", "Set至少需要一个成员")
                    return
                if self.is_edit:
                    success, msg = self.redis_model.update_set_value(key, members)
                else:
                    success, msg = self.redis_model.add_set_key(key, members, ttl)
            
            elif key_type == 'zset':
                text = self.zset_text.get("1.0", tk.END).strip()
                mapping = {}
                for line in text.split('\n'):
                    if '=' in line:
                        member, score = line.rsplit('=', 1)
                        mapping[member.strip()] = float(score.strip())
                if not mapping:
                    messagebox.showwarning("提示", "ZSet至少需要一个member=score")
                    return
                if self.is_edit:
                    success, msg = self.redis_model.update_zset_value(key, mapping)
                else:
                    success, msg = self.redis_model.add_zset_key(key, mapping, ttl)
            
            if success:
                messagebox.showinfo("成功", msg)
                self.result = True
                self.dialog.destroy()
            else:
                messagebox.showerror("错误", msg)
        
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def show(self) -> bool:
        """显示对话框"""
        self.dialog.wait_window()
        return self.result is not None
