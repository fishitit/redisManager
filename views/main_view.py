"""
主界面视图 - 三栏布局
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Callable, Optional


class MainView:
    """主界面视图"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Redis可视化管理工具")
        self.root.geometry("1200x700")
        self.root.minsize(900, 600)
        
        # 回调函数
        self.on_connect_callback = None
        self.on_disconnect_callback = None
        self.on_select_key_callback = None
        self.on_refresh_callback = None
        self.on_add_key_callback = None
        self.on_edit_key_callback = None
        self.on_delete_key_callback = None
        self.on_rename_key_callback = None
        self.on_set_ttl_callback = None
        self.on_flushdb_callback = None
        self.on_flushall_callback = None
        self.on_switch_db_callback = None
        self.on_manage_connections_callback = None
        self.on_show_client_list_callback = None
        self.on_get_key_detail_callback = None  # 获取key详情的回调
        self.on_auto_refresh_callback = None  # 自动刷新详情的回调
        
        # 状态变量
        self.connected_alias = tk.StringVar(value="未连接")
        self.current_db_var = tk.StringVar(value="0")
        self.db_size_var = tk.StringVar(value="")
        self.search_var = tk.StringVar()
        
        # 分页变量
        self.page_var = tk.StringVar(value="1")
        self.total_pages_var = tk.StringVar(value="0")
        self.total_keys_var = tk.StringVar(value="0")
        self.current_page = 1
        self.page_size = 50  # 默认50条
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置主界面"""
        # 顶部状态栏
        self.create_status_bar()
        
        # 主内容区 - 使用PanedWindow实现可调节大小的三栏布局
        self.paned_window = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 左侧：连接管理
        self.create_left_panel()

        # 中间：Key列表
        self.create_center_panel()

        # 右侧：详情/编辑区
        self.create_right_panel()
        
        # 设置初始面板宽度: 快捷操作120px, Key列表550px, Key详情550px
        self.root.update_idletasks()
        try:
            self.paned_window.sashpos(0, 120)
            self.paned_window.sashpos(1, 670)
        except:
            pass
    
    def create_status_bar(self):
        """创建顶部状态栏"""
        # 第一行：连接状态和数据库信息
        status_frame1 = ttk.Frame(self.root)
        status_frame1.pack(fill=tk.X, padx=5, pady=(5, 2))
        
        # 连接状态
        ttk.Label(status_frame1, text="状态:").pack(side=tk.LEFT)
        self.connection_label = ttk.Label(status_frame1, textvariable=self.connected_alias, 
                                         foreground="red")
        self.connection_label.pack(side=tk.LEFT, padx=5)
        
        # 数据库切换
        ttk.Label(status_frame1, text="数据库:").pack(side=tk.LEFT, padx=(20, 5))
        self.db_combo = ttk.Combobox(status_frame1, textvariable=self.current_db_var, 
                                     width=5, state="readonly")
        self.db_combo['values'] = [str(i) for i in range(16)]
        self.db_combo.current(0)
        self.db_combo.pack(side=tk.LEFT)
        self.db_combo.bind('<<ComboboxSelected>>', self.on_db_changed)
        
        # 数据库大小
        self.db_size_label = ttk.Label(status_frame1, textvariable=self.db_size_var)
        self.db_size_label.pack(side=tk.LEFT, padx=20)
        
        # 第二行：连接选择和操作按钮
        status_frame2 = ttk.Frame(self.root)
        status_frame2.pack(fill=tk.X, padx=5, pady=(2, 5))
        
        # 连接选择
        ttk.Label(status_frame2, text="选择连接:").pack(side=tk.LEFT)
        self.connection_combo = ttk.Combobox(status_frame2, width=20, state="readonly")
        self.connection_combo.pack(side=tk.LEFT, padx=5)
        self.connection_combo.bind('<<ComboboxSelected>>', self.on_connection_select)
        
        # 连接按钮
        ttk.Button(status_frame2, text="连接", command=self.on_connect).pack(side=tk.LEFT, padx=2)
        
        # 右侧按钮
        btn_frame = ttk.Frame(status_frame2)
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(btn_frame, text="管理连接", command=self.on_manage_connections).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="客户端列表", command=self.show_client_list).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="断开连接", command=self.on_disconnect).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="服务器信息", command=self.show_server_info).pack(side=tk.LEFT, padx=2)
    
    def create_left_panel(self):
        """创建左侧面板"""
        left_frame = ttk.LabelFrame(self.paned_window, text="快捷操作")
        # 允许面板根据内容自适应调整宽度

        # 操作按钮
        ttk.Button(left_frame, text="🔍 刷新", command=self.on_refresh).pack(fill=tk.X, pady=2, padx=2)
        ttk.Button(left_frame, text="➕ 新增Key", command=self.on_add_key).pack(fill=tk.X, pady=2, padx=2)
        ttk.Button(left_frame, text="✏️ 编辑", command=self.on_edit_key).pack(fill=tk.X, pady=2, padx=2)
        ttk.Button(left_frame, text="🗑️ 删除", command=self.on_delete_key).pack(fill=tk.X, pady=2, padx=2)
        ttk.Button(left_frame, text="💥 批量删除", command=self.on_batch_delete_key).pack(fill=tk.X, pady=2, padx=2)
        ttk.Button(left_frame, text="📝 重命名", command=self.on_rename_key).pack(fill=tk.X, pady=2, padx=2)
        ttk.Button(left_frame, text="⏰ 过期时间", command=self.on_set_ttl).pack(fill=tk.X, pady=2, padx=2)

        ttk.Separator(left_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8, padx=2)

        ttk.Button(left_frame, text="📤 导出连接", command=self.on_export_connections).pack(fill=tk.X, pady=2, padx=2)
        ttk.Button(left_frame, text="📥 导入连接", command=self.on_import_connections).pack(fill=tk.X, pady=2, padx=2)

        ttk.Separator(left_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8, padx=2)

        ttk.Button(left_frame, text="⚠️ 清空当前库", command=self.on_flushdb).pack(fill=tk.X, pady=2, padx=2)
        ttk.Button(left_frame, text="⚠️ 清空所有库", command=self.on_flushall).pack(fill=tk.X, pady=2, padx=2)

        # 添加到PanedWindow
        self.paned_window.add(left_frame, weight=0)
    
    def create_center_panel(self):
        """创建中间Key列表面板"""
        center_frame = ttk.LabelFrame(self.paned_window, text="Key列表")

        # 搜索栏
        search_frame = ttk.Frame(center_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 左侧：过滤条件
        left_search_frame = ttk.Frame(search_frame)
        left_search_frame.pack(side=tk.LEFT)

        ttk.Label(left_search_frame, text="过滤:").pack(side=tk.LEFT)
        search_entry = ttk.Entry(left_search_frame, textvariable=self.search_var, width=25)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind('<Return>', lambda e: self.on_search())
        
        # 类型过滤
        ttk.Label(left_search_frame, text="类型:").pack(side=tk.LEFT, padx=(5, 0))
        self.type_filter_var = tk.StringVar()
        self.type_filter_combo = ttk.Combobox(left_search_frame, textvariable=self.type_filter_var, width=8)
        self.type_filter_combo['values'] = ['全部', 'string', 'hash', 'list', 'set', 'zset']
        self.type_filter_combo.current(0)
        self.type_filter_combo.pack(side=tk.LEFT, padx=5)

        ttk.Button(left_search_frame, text="搜索", command=self.on_search).pack(side=tk.LEFT, padx=2)
        ttk.Button(left_search_frame, text="清空", command=self.clear_search).pack(side=tk.LEFT, padx=2)

        # Key列表
        list_frame = ttk.Frame(center_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 创建一个容器来支持水平滚动
        tree_container = ttk.Frame(list_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)

        self.key_tree = ttk.Treeview(tree_container, columns=('key', 'type', 'ttl', 'count'), show='headings', height=20, selectmode='extended')

        # 添加排序状态变量
        self.sort_column = None
        self.sort_reverse = False

        # 设置可排序的列标题
        self.key_tree.heading('key', text='Key', command=lambda: self.sort_key_list('key'))
        self.key_tree.heading('type', text='类型', command=lambda: self.sort_key_list('type'))
        self.key_tree.heading('ttl', text='TTL(秒)', command=lambda: self.sort_key_list('ttl'))
        self.key_tree.heading('count', text='个数', command=lambda: self.sort_key_list('count'))
        self.key_tree.column('key', width=280, minwidth=100, stretch=True)
        self.key_tree.column('type', width=70, minwidth=60, stretch=False)
        self.key_tree.column('ttl', width=80, minwidth=70, stretch=False)
        self.key_tree.column('count', width=70, minwidth=60, stretch=False)

        # 滚动条
        y_scroll = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.key_tree.yview)
        x_scroll = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.key_tree.xview)
        self.key_tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        # 使用grid布局让Treeview和滚动条正确配合
        self.key_tree.grid(row=0, column=0, sticky='nsew')
        y_scroll.grid(row=0, column=1, sticky='ns')
        x_scroll.grid(row=1, column=0, columnspan=2, sticky='ew')
        
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        # 绑定选择事件
        self.key_tree.bind('<<TreeviewSelect>>', lambda e: self.on_select_key(e))
        self.key_tree.bind('<Double-1>', lambda e: self.on_edit_key())
        
        # 绑定右键菜单
        self.key_tree.bind('<Button-3>', self.show_key_context_menu)  # Windows/Linux
        self.key_tree.bind('<Button-2>', self.show_key_context_menu)  # macOS

        # 创建右键菜单
        self.key_context_menu = tk.Menu(self.root, tearoff=0)
        self.key_context_menu.add_command(label="📋 复制Key", command=self.copy_selected_key)
        self.key_context_menu.add_command(label="📋 复制Value", command=self.copy_selected_key_value)
        self.key_context_menu.add_command(label="📋 复制完整信息", command=self.copy_selected_key_full)
        self.key_context_menu.add_separator()
        self.key_context_menu.add_command(label="✏️ 编辑Key", command=self.on_edit_key)
        self.key_context_menu.add_command(label="🗑️ 删除Key", command=self.on_delete_key)
        self.key_context_menu.add_command(label="📝 重命名Key", command=self.on_rename_key)
        self.key_context_menu.add_separator()
        self.key_context_menu.add_command(label="⏰ 设置过期时间", command=self.on_set_ttl)
        self.key_context_menu.add_command(label="🔄 刷新", command=self.on_refresh)

        # 分页栏
        page_frame = ttk.Frame(center_frame)
        page_frame.pack(fill=tk.X, padx=5, pady=(0, 5))

        # 左侧：翻页和页数信息
        left_page_frame = ttk.Frame(page_frame)
        left_page_frame.pack(side=tk.LEFT)

        # 每页条数设置（移到最左侧）
        ttk.Label(left_page_frame, text="每页显示:").pack(side=tk.LEFT)
        self.page_size_var = tk.StringVar(value="50")
        self.page_size_combo = ttk.Combobox(left_page_frame, textvariable=self.page_size_var, width=8)
        self.page_size_combo['values'] = ['10', '20', '50', '100', '200', '500']
        self.page_size_combo.current(2)  # 默认50
        self.page_size_combo.pack(side=tk.LEFT, padx=2)
        self.page_size_combo.bind('<<ComboboxSelected>>', self.on_page_size_change)

        ttk.Button(left_page_frame, text="上一页", command=self.prev_page).pack(side=tk.LEFT, padx=2)
        ttk.Label(left_page_frame, text="第").pack(side=tk.LEFT)

        # 当前页数输入框
        self.page_entry = ttk.Entry(left_page_frame, textvariable=self.page_var, width=5)
        self.page_entry.pack(side=tk.LEFT)
        self.page_entry.bind('<Return>', self.on_page_jump)

        ttk.Label(left_page_frame, text="页 / 共").pack(side=tk.LEFT)
        ttk.Label(left_page_frame, textvariable=self.total_pages_var, width=5).pack(side=tk.LEFT)
        ttk.Label(left_page_frame, text="页").pack(side=tk.LEFT)
        ttk.Button(left_page_frame, text="下一页", command=self.next_page).pack(side=tk.LEFT, padx=2)

        ttk.Separator(left_page_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)

        ttk.Label(left_page_frame, text="总计:").pack(side=tk.LEFT)
        ttk.Label(left_page_frame, textvariable=self.total_keys_var, width=8).pack(side=tk.LEFT)
        ttk.Label(left_page_frame, text="个Key").pack(side=tk.LEFT)
        
        # 添加到PanedWindow
        self.paned_window.add(center_frame, weight=1)
    
    def create_right_panel(self):
        """创建右侧详情面板"""
        right_frame = ttk.LabelFrame(self.paned_window, text="Key详情")

        # 信息区域
        info_frame = ttk.Frame(right_frame)
        info_frame.pack(fill=tk.X, padx=10, pady=10)

        # Key名称（可点击复制）
        ttk.Label(info_frame, text="Key:").grid(row=0, column=0, sticky=tk.W, pady=3)
        self.detail_key_var = tk.StringVar()
        self.detail_key_label = ttk.Label(info_frame, textvariable=self.detail_key_var, foreground="blue", cursor="hand2")
        self.detail_key_label.grid(row=0, column=1, sticky=tk.W, pady=3, padx=(5, 0))
        self.detail_key_label.bind('<Button-1>', lambda e: self.copy_detail_key_name())

        # 类型
        ttk.Label(info_frame, text="类型:").grid(row=1, column=0, sticky=tk.W, pady=3)
        self.detail_type_var = tk.StringVar()
        ttk.Label(info_frame, textvariable=self.detail_type_var).grid(row=1, column=1, sticky=tk.W, pady=3, padx=(5, 0))

        # 过期时间
        ttk.Label(info_frame, text="TTL:").grid(row=2, column=0, sticky=tk.W, pady=3)
        self.detail_ttl_var = tk.StringVar()
        ttk.Label(info_frame, textvariable=self.detail_ttl_var).grid(row=2, column=1, sticky=tk.W, pady=3, padx=(5, 0))

        # 个数
        ttk.Label(info_frame, text="个数:").grid(row=3, column=0, sticky=tk.W, pady=3)
        self.detail_count_var = tk.StringVar()
        ttk.Label(info_frame, textvariable=self.detail_count_var).grid(row=3, column=1, sticky=tk.W, pady=3, padx=(5, 0))

        # 自动刷新勾选
        self.auto_refresh_var = tk.BooleanVar(value=False)
        self.auto_refresh_cb = ttk.Checkbutton(info_frame, text="自动刷新（每秒）", variable=self.auto_refresh_var, command=self.on_auto_refresh_toggle)
        self.auto_refresh_cb.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=3)

        # 自动刷新定时器ID
        self._auto_refresh_job = None

        # 值显示区域
        value_frame = ttk.LabelFrame(right_frame, text="Value", padding="5")
        value_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # JSON操作按钮栏
        json_btn_frame = ttk.Frame(value_frame)
        json_btn_frame.pack(fill=tk.X, pady=(0, 5))
        
        # 左侧按钮
        left_btns = ttk.Frame(json_btn_frame)
        left_btns.pack(side=tk.LEFT)
        
        ttk.Button(left_btns, text="🔍 JSON校验", command=self.check_json).pack(side=tk.LEFT, padx=2)
        ttk.Button(left_btns, text="✨ 格式化JSON", command=self.format_json).pack(side=tk.LEFT, padx=2)
        ttk.Button(left_btns, text="📄 原始内容", command=self.show_raw_content).pack(side=tk.LEFT, padx=2)
        
        # 右侧状态标签
        self.json_status_var = tk.StringVar()
        self.json_status_label = ttk.Label(json_btn_frame, textvariable=self.json_status_var, foreground="green")
        self.json_status_label.pack(side=tk.RIGHT, padx=5)

        # 创建一个容器来支持水平滚动
        text_container = ttk.Frame(value_frame)
        text_container.pack(fill=tk.BOTH, expand=True)

        self.detail_text = tk.Text(text_container, height=15, width=40, state=tk.DISABLED, wrap=tk.NONE)
        detail_scroll_y = ttk.Scrollbar(text_container, orient=tk.VERTICAL, command=self.detail_text.yview)
        detail_scroll_x = ttk.Scrollbar(text_container, orient=tk.HORIZONTAL, command=self.detail_text.xview)
        self.detail_text.configure(yscrollcommand=detail_scroll_y.set, xscrollcommand=detail_scroll_x.set)

        # 使用grid布局
        self.detail_text.grid(row=0, column=0, sticky='nsew')
        detail_scroll_y.grid(row=0, column=1, sticky='ns')
        detail_scroll_x.grid(row=1, column=0, columnspan=2, sticky='ew')
        
        text_container.grid_rowconfigure(0, weight=1)
        text_container.grid_columnconfigure(0, weight=1)
        
        # 添加到PanedWindow
        self.paned_window.add(right_frame, weight=1)
    
    def set_connection_status(self, alias: str, connected: bool):
        """设置连接状态"""
        if connected:
            self.connected_alias.set(f"已连接（{alias}）")
            self.connection_label.config(foreground="green")
        else:
            self.connected_alias.set("未连接")
            self.connection_label.config(foreground="red")
    
    def update_db_size(self, size: int):
        """更新数据库大小显示"""
        self.db_size_var.set(f"Key数: {size}")
    
    def update_key_list(self, keys: list, total: int):
        """更新Key列表显示"""
        # 清空
        for item in self.key_tree.get_children():
            self.key_tree.delete(item)
        
        # 添加数据
        for key in keys:
            # 获取类型（从key字符串简单判断）
            key_str = str(key)
            key_type = "string"  # 默认值
            if ':' in key_str:
                # 尝试从命名规范推测类型
                pass
            self.key_tree.insert('', tk.END, values=(key, key_type))
        
        # 更新分页信息
        self.total_keys_var.set(str(total))
        total_pages = max(1, (total + self.page_size - 1) // self.page_size)
        self.total_pages_var.set(str(total_pages))
        self.page_var.set(str(self.current_page))
    
    def update_key_type_list(self, keys_with_types: list, total: int):
        """更新Key列表显示（带类型）"""
        for item in self.key_tree.get_children():
            self.key_tree.delete(item)
        
        for key, key_type in keys_with_types:
            self.key_tree.insert('', tk.END, values=(key, key_type, ''))
        
        self.total_keys_var.set(str(total))
        total_pages = max(1, (total + self.page_size - 1) // self.page_size)
        self.total_pages_var.set(str(total_pages))
        self.page_var.set(str(self.current_page))
    
    def update_key_list_with_ttl(self, keys_with_info: list, total: int):
        """更新Key列表显示（带类型和TTL）"""
        for item in self.key_tree.get_children():
            self.key_tree.delete(item)

        for key, key_type, ttl, count in keys_with_info:
            # 格式化TTL显示
            if ttl == -1:
                ttl_display = "永不过期"
            elif ttl == -2:
                ttl_display = "不存在"
            else:
                ttl_display = str(ttl)

            # 格式化个数显示
            count_display = str(count) if count else ""

            self.key_tree.insert('', tk.END, values=(key, key_type, ttl_display, count_display))

        self.total_keys_var.set(str(total))
        total_pages = max(1, (total + self.page_size - 1) // self.page_size)
        self.total_pages_var.set(str(total_pages))
        self.page_var.set(str(self.current_page))
    
    def set_key_detail(self, key: str, key_type: str, ttl: int, value: any, count: int = None):
        """设置Key详情"""
        self.detail_key_var.set(key)
        self.detail_type_var.set(key_type)

        if ttl == -1:
            self.detail_ttl_var.set("永不过期")
        elif ttl == -2:
            self.detail_ttl_var.set("Key不存在")
        else:
            self.detail_ttl_var.set(f"{ttl}秒")

        # 显示个数
        if count is not None:
            self.detail_count_var.set(str(count))
        else:
            self.detail_count_var.set("")
        
        # 显示值
        self.detail_text.config(state=tk.NORMAL)
        self.detail_text.delete("1.0", tk.END)
        
        # 缓存原始值用于JSON格式化
        self._current_detail_value = None

        if value is not None:
            if key_type == 'string':
                value_str = str(value)
                self._current_detail_value = value_str
                self.detail_text.insert(tk.END, value_str)
            elif key_type == 'hash':
                lines = []
                for field, val in value.items():
                    line = f"{field}: {val}"
                    lines.append(line)
                value_str = '\n'.join(lines)
                self._current_detail_value = value_str
                self.detail_text.insert(tk.END, value_str)
            elif key_type == 'list':
                lines = []
                for i, item in enumerate(value):
                    line = f"[{i}] {item}"
                    lines.append(line)
                value_str = '\n'.join(lines)
                self._current_detail_value = value_str
                self.detail_text.insert(tk.END, value_str)
            elif key_type == 'set':
                lines = []
                for item in value:
                    lines.append(str(item))
                value_str = '\n'.join(lines)
                self._current_detail_value = value_str
                self.detail_text.insert(tk.END, value_str)
            elif key_type == 'zset':
                lines = []
                for member, score in value:
                    lines.append(f"{member}: {score}")
                value_str = '\n'.join(lines)
                self._current_detail_value = value_str
                self.detail_text.insert(tk.END, value_str)
        
        self.detail_text.config(state=tk.DISABLED)
        
        # 重置JSON状态
        self.json_status_var.set("")
    
    def clear_key_detail(self):
        """清空Key详情"""
        self.detail_key_var.set("")
        self.detail_type_var.set("")
        self.detail_ttl_var.set("")
        self.detail_count_var.set("")
        self.detail_text.config(state=tk.NORMAL)
        self.detail_text.delete("1.0", tk.END)
        self.detail_text.config(state=tk.DISABLED)
        self.json_status_var.set("")
        self._current_detail_value = None  # 清空缓存的value
        # 停止自动刷新
        self.auto_refresh_var.set(False)
        self._stop_auto_refresh()
    
    def check_json(self):
        """JSON校验"""
        import json
        
        # 获取当前显示的内容
        self.detail_text.config(state=tk.NORMAL)
        content = self.detail_text.get("1.0", tk.END).strip()
        
        if not content:
            self.json_status_var.set("内容为空")
            self.json_status_label.config(foreground="gray")
            return
        
        # 尝试解析JSON
        try:
            json.loads(content)
            self.json_status_var.set("✓ JSON格式正确")
            self.json_status_label.config(foreground="green")
            messagebox.showinfo("JSON校验", "✓ JSON格式正确")
        except json.JSONDecodeError as e:
            self.json_status_var.set(f"✗ JSON错误: 第{e.lineno}行")
            self.json_status_label.config(foreground="red")
            messagebox.showerror("JSON校验", f"✗ JSON格式错误:\n第{e.lineno}行, 第{e.colno}列\n{e.msg}")
        
        self.detail_text.config(state=tk.DISABLED)
    
    def format_json(self):
        """格式化JSON"""
        import json
        
        if not hasattr(self, '_current_detail_value') or self._current_detail_value is None:
            messagebox.showwarning("提示", "没有可格式化的内容")
            return
        
        value_str = self._current_detail_value
        if not value_str:
            messagebox.showwarning("提示", "内容为空")
            return
        
        try:
            # 尝试解析JSON
            parsed = json.loads(value_str)
            # 格式化输出
            formatted = json.dumps(parsed, indent=2, ensure_ascii=False, sort_keys=False)
            
            # 显示格式化后的内容
            self.detail_text.config(state=tk.NORMAL)
            self.detail_text.delete("1.0", tk.END)
            self.detail_text.insert(tk.END, formatted)
            self.detail_text.config(state=tk.DISABLED)
            
            self.json_status_var.set("✓ JSON已格式化")
            self.json_status_label.config(foreground="green")
            
        except json.JSONDecodeError as e:
            messagebox.showerror("错误", f"无法解析JSON:\n第{e.lineno}行, 第{e.colno}列\n{e.msg}")
        except Exception as e:
            messagebox.showerror("错误", f"格式化失败: {str(e)}")
    
    def show_raw_content(self):
        """显示原始内容"""
        if hasattr(self, '_current_detail_value') and self._current_detail_value is not None:
            self.detail_text.config(state=tk.NORMAL)
            self.detail_text.delete("1.0", tk.END)
            self.detail_text.insert(tk.END, self._current_detail_value)
            self.detail_text.config(state=tk.DISABLED)
            self.json_status_var.set("✓ 已显示原始内容")
            self.json_status_label.config(foreground="blue")
    
    def on_auto_refresh_toggle(self):
        """自动刷新开关切换"""
        if self.auto_refresh_var.get():
            # 开始自动刷新
            self._start_auto_refresh()
        else:
            # 停止自动刷新
            self._stop_auto_refresh()

    def _start_auto_refresh(self):
        """启动自动刷新定时器"""
        self._stop_auto_refresh()  # 先停止已有的定时器
        self._auto_refresh_job = self.root.after(1000, self._auto_refresh_loop)

    def _auto_refresh_loop(self):
        """自动刷新循环"""
        if self.auto_refresh_var.get() and self.on_auto_refresh_callback:
            self.on_auto_refresh_callback()
        # 继续下一次循环
        if self.auto_refresh_var.get():
            self._auto_refresh_job = self.root.after(1000, self._auto_refresh_loop)

    def _stop_auto_refresh(self):
        """停止自动刷新定时器"""
        if self._auto_refresh_job:
            self.root.after_cancel(self._auto_refresh_job)
            self._auto_refresh_job = None

    def copy_detail_key_name(self):
        """复制详情面板中的Key名称"""
        key_name = self.detail_key_var.get()
        if key_name:
            self.root.clipboard_clear()
            self.root.clipboard_append(key_name)

    def get_selected_key(self) -> Optional[str]:
        """获取选中的Key（单选）"""
        selected = self.key_tree.selection()
        if selected:
            item = self.key_tree.item(selected[0])
            return item['values'][0]
        return None

    def get_selected_keys(self) -> list:
        """获取所有选中的Key列表（多选）"""
        selected = self.key_tree.selection()
        keys = []
        for item_id in selected:
            item = self.key_tree.item(item_id)
            keys.append(item['values'][0])
        return keys

    def on_batch_delete_key(self):
        """批量删除Key"""
        keys = self.get_selected_keys()
        if not keys:
            messagebox.showwarning("提示", "请先选择要删除的Key（可按住Ctrl/Cmd多选）")
            return

        key_list = "\n".join([f"  • {k}" for k in keys])
        if messagebox.askyesno("确认批量删除", f"确定要删除以下 {len(keys)} 个Key吗？\n\n{key_list}"):
            if self.on_batch_delete_key_callback:
                self.on_batch_delete_key_callback(keys)
    
    # 回调设置方法
    def on_connect(self):
        """连接Redis"""
        if self.on_connect_callback:
            # 获取选中的连接
            selected = self.connection_combo.get()
            if selected:
                self.on_connect_callback(selected)
            else:
                self.on_connect_callback()
    
    def on_connection_select(self, event=None):
        """选择连接时自动连接"""
        if self.on_connect_callback:
            selected = self.connection_combo.get()
            if selected:
                self.on_connect_callback(selected)
    
    def refresh_connection_list(self, connections: list):
        """刷新连接下拉列表"""
        aliases = [c['alias'] for c in connections]
        self.connection_combo['values'] = aliases
        if aliases:
            # 默认选择第一个
            self.connection_combo.current(0)
    
    def on_disconnect(self):
        if self.on_disconnect_callback:
            if messagebox.askyesno("确认", "确定要断开连接吗？"):
                self.on_disconnect_callback()
    
    def on_select_key(self, event):
        if self.on_select_key_callback:
            key = self.get_selected_key()
            if key:
                self.on_select_key_callback(key)
    
    def on_refresh(self):
        if self.on_refresh_callback:
            self.on_refresh_callback()
    
    def on_search(self):
        if self.on_refresh_callback:
            self.current_page = 1
            self.on_refresh_callback()
    
    def clear_search(self):
        """清空搜索框并刷新列表"""
        self.search_var.set("")  # 清空搜索框内容
        self.type_filter_var.set("全部")  # 重置类型过滤
        if self.on_refresh_callback:
            self.current_page = 1
            self.on_refresh_callback()
    
    def get_type_filter(self) -> str:
        """获取类型过滤条件"""
        type_filter = self.type_filter_var.get()
        if not type_filter or type_filter == '全部':
            return "*"
        return type_filter
    
    def sort_key_list(self, column: str):
        """Key列表排序"""
        # 切换排序方向
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        
        # 获取所有数据
        items = [(self.key_tree.set(item, column), item) for item in self.key_tree.get_children('')]
        
        # 尝试数字排序
        try:
            items.sort(key=lambda x: float(x[0]) if x[0] not in ['永不过期', '不存在', ''] else (0 if x[0] == '永不过期' else -1), reverse=self.sort_reverse)
        except ValueError:
            # 字符串排序
            items.sort(reverse=self.sort_reverse)
        
        # 重新排列
        for index, (val, item) in enumerate(items):
            self.key_tree.move(item, '', index)
        
        # 更新标题显示排序方向
        arrow = " ▲" if not self.sort_reverse else " ▼"
        self.key_tree.heading('key', text='Key' + (arrow if column == 'key' else ''))
        self.key_tree.heading('type', text='类型' + (arrow if column == 'type' else ''))
        self.key_tree.heading('ttl', text='TTL(秒)' + (arrow if column == 'ttl' else ''))
        self.key_tree.heading('count', text='个数' + (arrow if column == 'count' else ''))
    
    def show_key_context_menu(self, event):
        """显示Key右键菜单"""
        # 先选中右键点击的项
        item = self.key_tree.identify_row(event.y)
        if item:
            self.key_tree.selection_set(item)
            self.key_tree.focus(item)
            # 显示菜单
            self.key_context_menu.post(event.x_root, event.y_root)
        else:
            # 点击空白处
            self.key_context_menu.post(event.x_root, event.y_root)
    
    def copy_selected_key(self):
        """复制选中的Key名称"""
        key = self.get_selected_key()
        if key:
            self.root.clipboard_clear()
            self.root.clipboard_append(str(key))
            self.root.update()  # 确保剪贴板更新
            # 显示提示（可选）
            # messagebox.showinfo("成功", f"已复制Key: {key}")
    
    def copy_selected_key_value(self):
        """复制选中Key的Value内容"""
        key = self.get_selected_key()
        if not key:
            messagebox.showwarning("提示", "请先选择要复制的Key")
            return
        
        # 通过回调获取value
        if self.on_get_key_detail_callback:
            detail = self.on_get_key_detail_callback(key)
            if detail:
                value = detail.get('value')
                key_type = detail.get('type', '')
                
                if value is None:
                    messagebox.showwarning("提示", "Key没有Value")
                    return
                
                # 格式化value为文本
                value_text = self._format_value_for_copy(value, key_type)
                
                self.root.clipboard_clear()
                self.root.clipboard_append(value_text)
                self.root.update()
                messagebox.showinfo("成功", f"已复制Value到剪贴板")
                return
        
        messagebox.showerror("错误", "无法获取Value")
    
    def _format_value_for_copy(self, value, key_type: str) -> str:
        """格式化value为文本格式"""
        if key_type == 'string':
            return str(value)
        elif key_type == 'hash':
            lines = []
            for field, val in value.items():
                lines.append(f"{field}={val}")
            return '\n'.join(lines)
        elif key_type == 'list':
            return '\n'.join(str(item) for item in value)
        elif key_type == 'set':
            return '\n'.join(str(item) for item in value)
        elif key_type == 'zset':
            lines = []
            for member, score in value:
                lines.append(f"{member}={score}")
            return '\n'.join(lines)
        else:
            return str(value)
    
    def copy_selected_key_full(self):
        """复制选中Key的完整信息（包括value）"""
        key = self.get_selected_key()
        if not key:
            return
        
        # 从tree获取基本信息
        item = self.key_tree.selection()[0]
        values = self.key_tree.item(item)['values']
        key_name = values[0]
        key_type = values[1]
        key_ttl = values[2]
        
        # 通过回调获取value
        if self.on_get_key_detail_callback:
            detail = self.on_get_key_detail_callback(key)
            if detail:
                key_type = detail.get('type', key_type)
                ttl = detail.get('ttl', -1)
                if ttl == -1:
                    ttl_display = "永不过期"
                elif ttl == -2:
                    ttl_display = "不存在"
                else:
                    ttl_display = f"{ttl}秒"
                
                value = detail.get('value')
                
                # 构建完整信息
                info = f"Key: {key_name}\n类型: {key_type}\nTTL: {ttl_display}\n"
                
                # 格式化value
                if value is not None:
                    info += "\nValue:\n"
                    if key_type == 'string':
                        info += str(value)
                    elif key_type == 'hash':
                        for field, val in value.items():
                            info += f"  {field}: {val}\n"
                    elif key_type == 'list':
                        for i, item in enumerate(value):
                            info += f"  [{i}] {item}\n"
                    elif key_type == 'set':
                        for item in value:
                            info += f"  {item}\n"
                    elif key_type == 'zset':
                        for member, score in value:
                            info += f"  {member}: {score}\n"
                else:
                    info += "Value: (无)"
                
                self.root.clipboard_clear()
                self.root.clipboard_append(info)
                self.root.update()
                messagebox.showinfo("成功", "已复制Key完整信息到剪贴板")
                return
        
        # 如果没有回调，只复制基本信息
        info = f"Key: {key_name}\n类型: {key_type}\nTTL: {key_ttl}"
        self.root.clipboard_clear()
        self.root.clipboard_append(info)
        self.root.update()
    
    def on_add_key(self):
        if self.on_add_key_callback:
            self.on_add_key_callback()
    
    def on_edit_key(self):
        if self.on_edit_key_callback:
            key = self.get_selected_key()
            if key:
                self.on_edit_key_callback(key)
            else:
                messagebox.showwarning("提示", "请先选择要编辑的Key")
    
    def on_delete_key(self):
        if self.on_delete_key_callback:
            key = self.get_selected_key()
            if key:
                if messagebox.askyesno("确认删除", f"确定要删除Key '{key}' 吗？"):
                    self.on_delete_key_callback(key)
            else:
                messagebox.showwarning("提示", "请先选择要删除的Key")
    
    def on_rename_key(self):
        if self.on_rename_key_callback:
            key = self.get_selected_key()
            if key:
                self.on_rename_key_callback(key)
            else:
                messagebox.showwarning("提示", "请先选择要重命名的Key")
    
    def on_set_ttl(self):
        if self.on_set_ttl_callback:
            key = self.get_selected_key()
            if key:
                self.on_set_ttl_callback(key)
            else:
                messagebox.showwarning("提示", "请先选择Key")
    
    def on_flushdb(self):
        if self.on_flushdb_callback:
            if messagebox.askyesno("警告", "确定要清空当前数据库吗？此操作不可恢复！"):
                self.on_flushdb_callback()
    
    def on_flushall(self):
        if self.on_flushall_callback:
            if messagebox.askyesno("警告", "确定要清空所有数据库吗？此操作不可恢复！"):
                self.on_flushall_callback()
    
    def on_db_changed(self, event=None):
        if self.on_switch_db_callback:
            db = int(self.current_db_var.get())
            self.on_switch_db_callback(db)
    
    def on_manage_connections(self):
        if self.on_manage_connections_callback:
            self.on_manage_connections_callback()

    def on_export_connections(self):
        if self.on_export_connections_callback:
            self.on_export_connections_callback()

    def on_import_connections(self):
        if self.on_import_connections_callback:
            self.on_import_connections_callback()
    
    def prev_page(self):
        """上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            if self.on_refresh_callback:
                self.on_refresh_callback()

    def next_page(self):
        """下一页"""
        total = int(self.total_keys_var.get()) if self.total_keys_var.get().isdigit() else 0
        total_pages = max(1, (total + self.page_size - 1) // self.page_size)
        if self.current_page < total_pages:
            self.current_page += 1
            if self.on_refresh_callback:
                self.on_refresh_callback()
    
    def on_page_jump(self, event=None):
        """跳转到指定页"""
        try:
            page = int(self.page_var.get().strip())
            total = int(self.total_keys_var.get()) if self.total_keys_var.get().isdigit() else 0
            total_pages = max(1, (total + self.page_size - 1) // self.page_size)
            
            if page < 1:
                page = 1
            elif page > total_pages:
                page = total_pages
            
            self.page_var.set(str(page))
            self.current_page = page
            if self.on_refresh_callback:
                self.on_refresh_callback()
        except ValueError:
            # 输入无效，恢复原来的值
            self.page_var.set(str(self.current_page))
    
    def on_page_size_change(self, event=None):
        """改变每页显示条数"""
        try:
            new_size = int(self.page_size_var.get().strip())
            if new_size > 0:
                self.page_size = new_size
                self.current_page = 1  # 重置到第一页
                self.page_var.set("1")
                if self.on_refresh_callback:
                    self.on_refresh_callback()
        except ValueError:
            # 恢复原来的值
            self.page_size_var.set(str(self.page_size))
    
    def show_server_info(self):
        """显示服务器信息弹窗"""
        if hasattr(self, 'on_show_server_info_callback') and self.on_show_server_info_callback:
            self.on_show_server_info_callback()
    
    def show_client_list(self):
        """显示客户端列表"""
        if self.on_show_client_list_callback:
            self.on_show_client_list_callback()
    
    def show_server_info_dialog(self, info: dict):
        """显示服务器信息对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Redis服务器信息")
        dialog.geometry("500x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - 500) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 600) // 2
        dialog.geometry(f"500x600+{x}+{y}")
        
        # 内容
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        text = tk.Text(main_frame, height=25, width=55)
        scroll = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 格式化显示
        for key, val in info.items():
            key_display = key.replace('_', ' ').title()
            text.insert(tk.END, f"{key_display}: {val}\n")
        
        text.config(state=tk.DISABLED)
        
        ttk.Button(dialog, text="关闭", command=dialog.destroy).pack(pady=10)
    
    def show_rename_dialog(self, old_key: str) -> Optional[str]:
        """显示重命名对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("重命名Key")
        dialog.geometry("400x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - 400) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 150) // 2
        dialog.geometry(f"400x150+{x}+{y}")
        
        result = [None]
        
        ttk.Label(dialog, text=f"原Key: {old_key}").pack(pady=10)
        
        new_key_var = tk.StringVar()
        ttk.Label(dialog, text="新Key名称:").pack()
        ttk.Entry(dialog, textvariable=new_key_var, width=40).pack(pady=5)
        
        def on_ok():
            new_key = new_key_var.get().strip()
            if new_key:
                result[0] = new_key
                dialog.destroy()
            else:
                messagebox.showwarning("提示", "Key名称不能为空")
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="确定", command=on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        dialog.wait_window()
        return result[0]
    
    def show_ttl_dialog(self, key: str) -> Optional[int]:
        """显示设置TTL对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("设置过期时间")
        dialog.geometry("350x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - 350) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 150) // 2
        dialog.geometry(f"350x150+{x}+{y}")
        
        result = [None]
        
        ttk.Label(dialog, text=f"Key: {key}").pack(pady=5)
        
        ttl_var = tk.StringVar()
        ttk.Label(dialog, text="过期时间(秒，0表示移除过期):").pack()
        ttk.Entry(dialog, textvariable=ttl_var, width=30).pack(pady=5)
        
        def on_ok():
            try:
                ttl = int(ttl_var.get().strip())
                if ttl >= 0:
                    result[0] = ttl
                    dialog.destroy()
                else:
                    messagebox.showwarning("提示", "过期时间不能为负数")
            except ValueError:
                messagebox.showerror("错误", "请输入有效数字")
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="确定", command=on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        dialog.wait_window()
        return result[0]
