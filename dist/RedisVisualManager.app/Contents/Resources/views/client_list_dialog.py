"""
客户端列表对话框 - 查看当前连接的Redis客户端
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional


class ClientListDialog:
    """客户端列表对话框"""
    
    def __init__(self, parent, redis_model):
        self.parent = parent
        self.redis_model = redis_model
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("客户端连接列表")
        self.dialog.geometry("1200x550")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.center_window()
        self.setup_ui()
        self.load_client_list()

    def center_window(self):
        """窗口居中"""
        self.dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() - 1200) // 2
        y = self.parent.winfo_y() + (self.parent.winfo_height() - 550) // 2
        self.dialog.geometry(f"1200x550+{x}+{y}")
    
    def setup_ui(self):
        """设置界面"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 顶部控制面板
        control_frame = ttk.LabelFrame(main_frame, text="过滤和搜索", padding="5")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # IP过滤
        ttk.Label(control_frame, text="IP地址:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.ip_filter_var = tk.StringVar()
        self.ip_filter_entry = ttk.Entry(control_frame, textvariable=self.ip_filter_var, width=20)
        self.ip_filter_entry.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # 数据库过滤
        ttk.Label(control_frame, text="数据库:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.db_filter_var = tk.StringVar()
        self.db_filter_combo = ttk.Combobox(control_frame, textvariable=self.db_filter_var, width=5)
        self.db_filter_combo['values'] = ['全部'] + [str(i) for i in range(16)]
        self.db_filter_combo.current(0)
        self.db_filter_combo.grid(row=0, column=3, sticky=tk.W, padx=5)
        
        # 客户端类型过滤
        ttk.Label(control_frame, text="类型:").grid(row=0, column=4, sticky=tk.W, padx=5)
        self.type_filter_var = tk.StringVar()
        self.type_filter_combo = ttk.Combobox(control_frame, textvariable=self.type_filter_var, width=10)
        self.type_filter_combo['values'] = ['全部', '正常连接', '主从复制', '发布订阅']
        self.type_filter_combo.current(0)
        self.type_filter_combo.grid(row=0, column=5, sticky=tk.W, padx=5)
        
        # 搜索和刷新按钮
        ttk.Button(control_frame, text="🔍 搜索", command=self.load_client_list).grid(row=0, column=6, padx=5)
        ttk.Button(control_frame, text="🔄 刷新", command=self.load_client_list).grid(row=0, column=7, padx=5)
        
        # 统计信息
        self.stats_label = ttk.Label(control_frame, text="", font=("", 10, "bold"))
        self.stats_label.grid(row=0, column=8, padx=(20, 5))
        
        # 客户端列表
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 扩展的列
        columns = ('id', 'addr', 'ip', 'port', 'age', 'idle', 'flags', 'db', 'name', 'cmd')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        self.tree.heading('id', text='ID')
        self.tree.heading('addr', text='完整地址')
        self.tree.heading('ip', text='IP地址')
        self.tree.heading('port', text='端口')
        self.tree.heading('age', text='连接时长(秒)')
        self.tree.heading('idle', text='空闲时间(秒)')
        self.tree.heading('flags', text='类型')
        self.tree.heading('db', text='数据库')
        self.tree.heading('name', text='客户端名称')
        self.tree.heading('cmd', text='最后命令')
        
        self.tree.column('id', width=60, anchor='center')
        self.tree.column('addr', width=200)
        self.tree.column('ip', width=130)
        self.tree.column('port', width=70, anchor='center')
        self.tree.column('age', width=120, anchor='e')
        self.tree.column('idle', width=110, anchor='e')
        self.tree.column('flags', width=80, anchor='center')
        self.tree.column('db', width=60, anchor='center')
        self.tree.column('name', width=150)
        self.tree.column('cmd', width=150)
        
        # 滚动条
        y_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        x_scroll = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 绑定双击事件查看详情
        self.tree.bind('<Double-1>', self.show_client_detail)
        
        # 底部按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="📋 详细信息", command=self.show_client_detail).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="⚠️ 断开选中连接", command=self.kill_selected).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="关闭", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def load_client_list(self):
        """加载客户端列表"""
        # 清空
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            # 获取数据
            clients = self.redis_model.get_client_list()
            
            if clients is None:
                self.stats_label.config(text="获取失败: 未连接到Redis")
                messagebox.showerror("错误", "请先连接Redis")
                return
            
            if len(clients) == 0:
                self.stats_label.config(text="无客户端连接")
                return
            
            print(f"调试: 获取到 {len(clients)} 个客户端连接")
            if clients:
                print(f"调试: 第一个连接数据: {clients[0]}")
            
            # 获取过滤条件
            ip_filter = self.ip_filter_var.get().strip()
            db_filter = self.db_filter_var.get()
            if not db_filter:
                db_filter = '全部'
            type_filter = self.type_filter_var.get()
            if not type_filter:
                type_filter = '全部'
            
            print(f"调试: 过滤条件 - IP: '{ip_filter}', DB: '{db_filter}', Type: '{type_filter}'")
            
            # 过滤和显示数据
            filtered_count = 0
            total_idle = 0
            total_age = 0
            
            for client in clients:
                # 解析地址
                addr = client.get('addr', '')
                ip = ''
                port = ''
                if ':' in addr:
                    parts = addr.rsplit(':', 1)
                    ip = parts[0]
                    port = parts[1]
                
                # 应用过滤
                if ip_filter and ip_filter not in ip:
                    print(f"调试: 过滤掉 {addr} - IP不匹配")
                    continue
                
                client_db = str(client.get('db', ''))
                if db_filter != '全部' and client_db != db_filter:
                    print(f"调试: 过滤掉 {addr} - DB不匹配 (client_db={client_db}, filter={db_filter})")
                    continue
                
                # 类型过滤
                flags = client.get('flags', '')
                if type_filter == '正常连接' and flags != 'N':
                    continue
                elif type_filter == '主从复制' and 'S' not in flags:
                    continue
                elif type_filter == '发布订阅' and 'P' not in flags:
                    continue
                
                # 解析类型显示
                if flags == 'N':
                    type_display = '正常'
                elif 'M' in flags:
                    type_display = '主节点'
                elif 'S' in flags:
                    type_display = '从节点'
                elif 'P' in flags:
                    type_display = '发布订阅'
                else:
                    type_display = flags
                
                # 插入数据
                values = (
                    client.get('id', ''),
                    addr,
                    ip,
                    port,
                    client.get('age', ''),
                    client.get('idle', ''),
                    type_display,
                    client.get('db', ''),
                    client.get('name', ''),
                    client.get('cmd', '')
                )
                
                self.tree.insert('', tk.END, values=values)
                
                filtered_count += 1
                try:
                    total_idle += int(float(client.get('idle', 0)))
                    total_age += int(float(client.get('age', 0)))
                except:
                    pass
            
            print(f"调试: 过滤后显示 {filtered_count} 个连接")
            
            # 更新统计
            total = len(clients)
            stats_text = f"总连接: {total} | 显示: {filtered_count}"
            if filtered_count > 0:
                avg_idle = total_idle // filtered_count
                stats_text += f" | 平均空闲: {avg_idle}秒"
            self.stats_label.config(text=stats_text)
            
        except Exception as e:
            print(f"加载客户端列表异常: {e}")
            import traceback
            traceback.print_exc()
            self.stats_label.config(text=f"加载失败: {str(e)}")
            messagebox.showerror("错误", f"加载客户端列表失败:\n{str(e)}")
    
    def kill_selected(self):
        """断开选中的连接"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要断开的连接")
            return
        
        item = self.tree.item(selected[0])
        addr = item['values'][1]
        client_id = item['values'][0]
        
        if messagebox.askyesno("确认断开", f"确定要断开以下连接吗？\n\n"
                               f"ID: {client_id}\n"
                               f"地址: {addr}"):
            success, msg = self.redis_model.kill_client(addr)
            if success:
                messagebox.showinfo("成功", msg)
                self.load_client_list()
            else:
                messagebox.showerror("错误", msg)
    
    def show_client_detail(self, event=None):
        """显示客户端详细信息"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择一个连接")
            return
        
        item = self.tree.item(selected[0])
        client_id = item['values'][0]
        addr = item['values'][1]
        
        # 获取原始数据
        clients = self.redis_model.get_client_list()
        client_data = None
        for c in clients:
            if str(c.get('id')) == str(client_id):
                client_data = c
                break
        
        if not client_data:
            messagebox.showerror("错误", "无法获取客户端详细信息")
            return
        
        # 创建详情窗口
        detail_dialog = tk.Toplevel(self.dialog)
        detail_dialog.title(f"客户端详情 - {addr}")
        detail_dialog.geometry("600x500")
        detail_dialog.transient(self.dialog)
        detail_dialog.grab_set()
        
        # 居中
        detail_dialog.update_idletasks()
        x = self.dialog.winfo_x() + (self.dialog.winfo_width() - 600) // 2
        y = self.dialog.winfo_y() + (self.dialog.winfo_height() - 500) // 2
        detail_dialog.geometry(f"600x500+{x}+{y}")
        
        # 显示所有字段
        main_frame = ttk.Frame(detail_dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 基本信息
        info_frame = ttk.LabelFrame(main_frame, text="连接信息", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        fields = [
            ('ID', 'id'),
            ('完整地址', 'addr'),
            ('创建时间', 'create_time'),
            ('连接时长(秒)', 'age'),
            ('空闲时间(秒)', 'idle'),
            ('标志/类型', 'flags'),
            ('数据库', 'db'),
            ('客户端名称', 'name'),
            ('最后命令', 'cmd'),
            ('命令总数', 'tot-cmds'),
            ('键命中次数', 'keyhits'),
        ]
        
        row = 0
        for label, field in fields:
            value = client_data.get(field, 'N/A')
            ttk.Label(info_frame, text=f"{label}:", width=15, anchor=tk.W).grid(row=row, column=0, sticky=tk.W, pady=3)
            ttk.Label(info_frame, text=str(value), foreground="blue").grid(row=row, column=1, sticky=tk.W, pady=3, padx=(10, 0))
            row += 1
        
        # 网络信息
        net_frame = ttk.LabelFrame(main_frame, text="网络信息", padding="10")
        net_frame.pack(fill=tk.X, pady=(0, 10))
        
        network_fields = [
            ('输入缓冲字节', 'obl'),
            ('输出缓冲字节', 'obb'),
            ('输出内存字节', 'omem'),
            ('文件描述符', 'fd'),
        ]
        
        row = 0
        for label, field in network_fields:
            value = client_data.get(field, 'N/A')
            ttk.Label(net_frame, text=f"{label}:", width=15, anchor=tk.W).grid(row=row, column=0, sticky=tk.W, pady=3)
            ttk.Label(net_frame, text=str(value)).grid(row=row, column=1, sticky=tk.W, pady=3, padx=(10, 0))
            row += 1
        
        # 按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        def kill_this():
            if messagebox.askyesno("确认", f"确定要断开连接 {addr} 吗？"):
                success, msg = self.redis_model.kill_client(addr)
                if success:
                    messagebox.showinfo("成功", msg)
                    detail_dialog.destroy()
                    self.load_client_list()
                else:
                    messagebox.showerror("错误", msg)
        
        ttk.Button(btn_frame, text="⚠️ 断开此连接", command=kill_this).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="关闭", command=detail_dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def show(self):
        """显示对话框"""
        self.dialog.wait_window()
