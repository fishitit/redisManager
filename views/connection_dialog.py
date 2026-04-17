"""
连接管理对话框视图
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Dict


class ConnectionDialog:
    """连接管理对话框"""
    
    def __init__(self, parent, connection_model, on_save=None):
        self.parent = parent
        self.model = connection_model
        self.on_save = on_save
        self.result = None
        
        # 创建顶层窗口
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("连接管理")
        self.dialog.geometry("700x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中显示
        self.center_window()
        
        self.setup_ui()
        self.load_connections()
    
    def center_window(self):
        """窗口居中"""
        self.dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() - 700) // 2
        y = self.parent.winfo_y() + (self.parent.winfo_height() - 500) // 2
        self.dialog.geometry(f"700x500+{x}+{y}")
    
    def setup_ui(self):
        """设置界面"""
        # 主框架
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧连接列表
        left_frame = ttk.LabelFrame(main_frame, text="已保存的连接", padding="5")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # 连接列表Treeview（支持多选）
        columns = ('alias', 'host', 'port', 'db')
        self.tree = ttk.Treeview(left_frame, columns=columns, show='headings', height=15, selectmode='extended')
        self.tree.heading('alias', text='别名')
        self.tree.heading('host', text='主机')
        self.tree.heading('port', text='端口')
        self.tree.heading('db', text='数据库')
        self.tree.column('alias', width=120)
        self.tree.column('host', width=100)
        self.tree.column('port', width=60)
        self.tree.column('db', width=60)
        
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定选择事件
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
        # 右侧操作区
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        
        # 按钮区域（上）
        btn_top_frame = ttk.Frame(right_frame)
        btn_top_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(btn_top_frame, text="添加", command=self.add_connection).pack(fill=tk.X, pady=2)
        ttk.Button(btn_top_frame, text="编辑", command=self.edit_connection).pack(fill=tk.X, pady=2)
        ttk.Button(btn_top_frame, text="删除", command=self.delete_connection).pack(fill=tk.X, pady=2)
        
        ttk.Separator(btn_top_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_top_frame, text="📤 导出", command=self.export_connections).pack(fill=tk.X, pady=2)
        ttk.Button(btn_top_frame, text="📥 导入", command=self.import_connections).pack(fill=tk.X, pady=2)
        
        # 编辑表单区域
        form_frame = ttk.LabelFrame(right_frame, text="连接信息", padding="10")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # 别名
        ttk.Label(form_frame, text="别名:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.alias_var = tk.StringVar()
        self.alias_entry = ttk.Entry(form_frame, textvariable=self.alias_var, width=25)
        self.alias_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # 主机
        ttk.Label(form_frame, text="主机:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.host_var = tk.StringVar(value="127.0.0.1")
        self.host_entry = ttk.Entry(form_frame, textvariable=self.host_var, width=25)
        self.host_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # 端口
        ttk.Label(form_frame, text="端口:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.port_var = tk.StringVar(value="6379")
        self.port_entry = ttk.Entry(form_frame, textvariable=self.port_var, width=25)
        self.port_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # 密码
        ttk.Label(form_frame, text="密码:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(form_frame, textvariable=self.password_var, width=25, show="*")
        self.password_entry.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # 数据库
        ttk.Label(form_frame, text="数据库:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.db_var = tk.StringVar(value="0")
        self.db_entry = ttk.Entry(form_frame, textvariable=self.db_var, width=25)
        self.db_entry.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # 底部按钮
        btn_bottom_frame = ttk.Frame(right_frame)
        btn_bottom_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_bottom_frame, text="保存", command=self.save_form).pack(fill=tk.X, pady=2)
        ttk.Button(btn_bottom_frame, text="测试连接", command=self.test_connection).pack(fill=tk.X, pady=2)
        ttk.Button(btn_bottom_frame, text="关闭", command=self.dialog.destroy).pack(fill=tk.X, pady=2)
        
        # 记录当前选中项
        self.current_selection = None
    
    def load_connections(self):
        """加载连接列表"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for conn in self.model.get_all_connections():
            self.tree.insert('', tk.END, values=(
                conn['alias'],
                conn['host'],
                conn['port'],
                conn['db']
            ))
    
    def on_select(self, event):
        """选择连接时填充表单"""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            values = item['values']
            self.current_selection = values[0]
            
            # 获取完整信息
            conn = self.model.get_connection(values[0])
            if conn:
                self.alias_var.set(conn['alias'])
                self.host_var.set(conn['host'])
                self.port_var.set(str(conn['port']))
                self.password_var.set(conn.get('password', ''))
                self.db_var.set(str(conn['db']))
    
    def add_connection(self):
        """添加连接"""
        self.current_selection = None
        self.alias_var.set("")
        self.host_var.set("127.0.0.1")
        self.port_var.set("6379")
        self.password_var.set("")
        self.db_var.set("0")
        self.alias_entry.focus()
    
    def edit_connection(self):
        """编辑连接"""
        if not self.current_selection:
            messagebox.showwarning("提示", "请先选择要编辑的连接")
            return
        # 表单已经填充，直接编辑即可
    
    def delete_connection(self):
        """删除连接（支持批量删除）"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要删除的连接")
            return

        # 获取所有选中的连接别名
        aliases = []
        for item in selected:
            values = self.tree.item(item)['values']
            aliases.append(values[0])

        # 根据选中数量显示不同的确认信息
        if len(aliases) == 1:
            confirm_msg = f"确定要删除连接 '{aliases[0]}' 吗？"
        else:
            confirm_msg = f"确定要删除以下 {len(aliases)} 个连接吗？\n\n" + "\n".join(aliases)

        if messagebox.askyesno("确认删除", confirm_msg):
            success_count = 0
            fail_count = 0
            
            for alias in aliases:
                if self.model.delete_connection(alias):
                    success_count += 1
                else:
                    fail_count += 1

            # 重新加载列表
            self.load_connections()
            self.alias_var.set("")
            self.host_var.set("127.0.0.1")
            self.port_var.set("6379")
            self.password_var.set("")
            self.db_var.set("0")
            self.current_selection = None

            # 显示删除结果
            result_msg = f"删除完成\n成功: {success_count} 个"
            if fail_count > 0:
                result_msg += f"\n失败: {fail_count} 个"
            messagebox.showinfo("删除结果", result_msg)
    
    def test_connection(self):
        """测试连接"""
        try:
            import redis
            host = self.host_var.get().strip()
            port = int(self.port_var.get().strip())
            password = self.password_var.get().strip()
            
            client = redis.Redis(
                host=host,
                port=port,
                password=password if password else None,
                socket_connect_timeout=5
            )
            client.ping()
            messagebox.showinfo("测试连接", "连接成功！")
        except ValueError:
            messagebox.showerror("错误", "端口必须是数字")
        except redis.ConnectionError:
            messagebox.showerror("错误", f"无法连接到 {host}:{port}")
        except redis.AuthenticationError:
            messagebox.showerror("错误", "认证失败，密码错误")
        except Exception as e:
            messagebox.showerror("错误", f"连接失败: {str(e)}")
    
    def get_form_data(self) -> Optional[Dict]:
        """获取表单数据"""
        try:
            alias = self.alias_var.get().strip()
            host = self.host_var.get().strip()
            port = int(self.port_var.get().strip())
            password = self.password_var.get().strip()
            db = int(self.db_var.get().strip())
            
            if not alias:
                messagebox.showwarning("提示", "别名不能为空")
                return None
            
            if not host:
                messagebox.showwarning("提示", "主机不能为空")
                return None
            
            if port < 1 or port > 65535:
                messagebox.showwarning("提示", "端口范围: 1-65535")
                return None
            
            if db < 0 or db > 15:
                messagebox.showwarning("提示", "数据库范围: 0-15")
                return None
            
            return {
                'alias': alias,
                'host': host,
                'port': port,
                'password': password,
                'db': db
            }
        except ValueError:
            messagebox.showerror("错误", "端口和数据库必须是数字")
            return None
    
    def save_form(self):
        """保存当前表单"""
        data = self.get_form_data()
        if not data:
            return False
        
        if self.current_selection:
            # 更新
            if self.model.update_connection(self.current_selection, **data):
                self.load_connections()
                self.current_selection = data['alias']
                messagebox.showinfo("成功", "连接配置已更新")
                return True
            else:
                messagebox.showerror("错误", "更新失败")
                return False
        else:
            # 添加
            if self.model.add_connection(**data):
                self.load_connections()
                self.current_selection = data['alias']
                messagebox.showinfo("成功", f"连接配置 '{data['alias']}' 已添加")
                return True
            else:
                messagebox.showerror("错误", "别名已存在")
                return False
    
    def show(self):
        """显示对话框并等待关闭"""
        self.dialog.wait_window()

    def export_connections(self):
        """导出连接配置到文件"""
        file_path = filedialog.asksaveasfilename(
            title="导出连接配置",
            defaultextension=".json",
            filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")],
            initialfile="redis_connections.json"
        )
        
        if file_path:
            if self.model.export_connections(file_path):
                messagebox.showinfo("成功", f"连接配置已导出到:\n{file_path}")
            else:
                messagebox.showerror("错误", "导出失败")

    def import_connections(self):
        """从文件导入连接配置"""
        file_path = filedialog.askopenfilename(
            title="导入连接配置",
            filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if file_path:
            success, msg = self.model.import_connections(file_path)
            if success:
                self.load_connections()
                messagebox.showinfo("成功", msg)
            else:
                messagebox.showerror("错误", msg)
