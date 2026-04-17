"""
控制器 - 连接视图和模型
"""
import os
from models import ConnectionModel, RedisModel
from views import MainView, ConnectionDialog, AddKeyDialog
from tkinter import messagebox, filedialog


class Controller:
    """主控制器"""
    
    def __init__(self, root):
        self.root = root
        self.connection_model = ConnectionModel()
        self.redis_model = RedisModel()
        self.view = MainView(root)
        
        # 当前连接配置
        self.current_connection = None
        
        self.bind_events()
    
    def bind_events(self):
        """绑定事件回调"""
        self.view.on_manage_connections_callback = self.manage_connections
        self.view.on_connect_callback = self.connect
        self.view.on_disconnect_callback = self.disconnect
        self.view.on_refresh_callback = self.refresh_keys
        self.view.on_select_key_callback = self.select_key
        self.view.on_add_key_callback = self.add_key
        self.view.on_edit_key_callback = self.edit_key
        self.view.on_delete_key_callback = self.delete_key
        self.view.on_batch_delete_key_callback = self.batch_delete_key
        self.view.on_rename_key_callback = self.rename_key
        self.view.on_set_ttl_callback = self.set_ttl
        self.view.on_flushdb_callback = self.flushdb
        self.view.on_flushall_callback = self.flushall
        self.view.on_switch_db_callback = self.switch_db
        self.view.on_show_server_info_callback = self.show_server_info
        self.view.on_show_client_list_callback = self.show_client_list
        self.view.on_get_key_detail_callback = self.get_key_detail_for_copy
        self.view.on_auto_refresh_callback = self.auto_refresh_key_detail
        self.view.on_export_connections_callback = self.export_connections
        self.view.on_import_connections_callback = self.import_connections
        
        # 初始化连接列表
        self.refresh_connection_list()
    
    def manage_connections(self):
        """管理连接"""
        dialog = ConnectionDialog(self.root, self.connection_model)
        dialog.show()
        
        # 刷新连接列表
        self.refresh_connection_list()
    
    def refresh_connection_list(self):
        """刷新连接列表显示"""
        connections = self.connection_model.get_all_connections()
        self.view.refresh_connection_list(connections)
    
    def connect(self, alias: str = None):
        """连接Redis"""
        # 如果没有指定alias，尝试使用选中的或第一个
        if not alias:
            # 尝试从下拉框获取选中的
            selected = self.view.connection_combo.get()
            if selected:
                alias = selected
            else:
                # 使用第一个连接
                connections = self.connection_model.get_all_connections()
                if not connections:
                    messagebox.showwarning("提示", "请先添加Redis连接配置")
                    self.manage_connections()
                    return
                alias = connections[0]['alias']
        
        conn = self.connection_model.get_connection(alias)
        if not conn:
            messagebox.showerror("错误", f"连接配置 '{alias}' 不存在")
            return
        
        success, msg = self.redis_model.connect(
            conn['host'],
            conn['port'],
            conn.get('password', ''),
            conn['db']
        )
        
        if success:
            self.current_connection = conn
            self.view.set_connection_status(alias, True)
            self.view.current_db_var.set(str(conn['db']))
            self.refresh_keys()
            messagebox.showinfo("成功", f"已连接到 {alias}")
        else:
            messagebox.showerror("错误", msg)
    
    def quick_connect(self, conn: dict):
        """快速连接（从连接管理界面）"""
        success, msg = self.redis_model.connect(
            conn['host'],
            conn['port'],
            conn.get('password', ''),
            conn['db']
        )
        
        if success:
            self.current_connection = conn
            self.view.set_connection_status(conn['alias'], True)
            self.view.current_db_var.set(str(conn['db']))
            self.refresh_keys()
        else:
            messagebox.showerror("错误", msg)
    
    def disconnect(self):
        """断开连接"""
        self.redis_model.disconnect()
        self.current_connection = None
        self.view.set_connection_status("未连接", False)
        self.view.clear_key_detail()
        self.view.update_key_list([], 0)
        self.view.update_db_size(0)
        # 清空连接选择
        self.view.connection_combo.current(-1)
    
    def refresh_keys(self):
        """刷新Key列表"""
        if not self.redis_model.connected:
            return
        
        pattern = "*"
        search_text = self.view.search_var.get().strip()
        if search_text:
            pattern = f"*{search_text}*"
        
        # 获取类型过滤
        type_filter = self.view.get_type_filter()
        
        # 使用新的方法获取带类型和TTL的信息
        keys_with_info, total = self.redis_model.get_keys_with_info(
            pattern=pattern,
            page=self.view.current_page,
            page_size=self.view.page_size
        )
        
        # 如果有类型过滤，在客户端过滤
        if type_filter != "*":
            keys_with_info = [(k, t, ttl) for k, t, ttl in keys_with_info if t == type_filter]
            total = len(keys_with_info)
        
        self.view.update_key_list_with_ttl(keys_with_info, total)

        # 更新数据库大小
        db_size = self.redis_model.db_size()
        self.view.update_db_size(db_size)
    
    def select_key(self, key: str):
        """选中Key时显示详情"""
        if not self.redis_model.connected:
            return

        key_type = self.redis_model.get_key_type(key)
        ttl = self.redis_model.get_key_ttl(key)
        value = self.redis_model.get_key_value(key)
        count = self.redis_model.get_key_count(key, key_type)

        self.view.set_key_detail(key, key_type, ttl, value, count)

    def auto_refresh_key_detail(self):
        """自动刷新当前选中的Key详情"""
        if not self.redis_model.connected:
            return

        key = self.view.detail_key_var.get()
        if not key:
            return

        key_type = self.redis_model.get_key_type(key)
        ttl = self.redis_model.get_key_ttl(key)
        value = self.redis_model.get_key_value(key)
        count = self.redis_model.get_key_count(key, key_type)

        self.view.set_key_detail(key, key_type, ttl, value, count)

    def add_key(self):
        """新增Key"""
        if not self.redis_model.connected:
            messagebox.showwarning("提示", "请先连接Redis")
            return
        
        dialog = AddKeyDialog(self.root, self.redis_model)
        if dialog.show():
            self.refresh_keys()
    
    def edit_key(self, key: str):
        """编辑Key"""
        if not self.redis_model.connected:
            return
        
        key_type = self.redis_model.get_key_type(key)
        dialog = AddKeyDialog(self.root, self.redis_model, key=key, key_type=key_type)
        if dialog.show():
            self.refresh_keys()
            self.select_key(key)
    
    def delete_key(self, key: str):
        """删除Key"""
        if not self.redis_model.connected:
            return

        if self.redis_model.delete_key(key):
            messagebox.showinfo("成功", f"Key '{key}' 已删除")
            self.refresh_keys()
            self.view.clear_key_detail()
        else:
            messagebox.showerror("错误", "删除失败")

    def batch_delete_key(self, keys: list):
        """批量删除Key"""
        if not self.redis_model.connected:
            return

        success_count = 0
        fail_count = 0
        for key in keys:
            if self.redis_model.delete_key(key):
                success_count += 1
            else:
                fail_count += 1

        msg = f"批量删除完成\n成功: {success_count} 个"
        if fail_count > 0:
            msg += f"\n失败: {fail_count} 个"
        messagebox.showinfo("批量删除", msg)
        self.refresh_keys()
        self.view.clear_key_detail()
    
    def rename_key(self, old_key: str):
        """重命名Key"""
        if not self.redis_model.connected:
            return
        
        new_key = self.view.show_rename_dialog(old_key)
        if new_key:
            success, msg = self.redis_model.rename_key(old_key, new_key)
            if success:
                messagebox.showinfo("成功", msg)
                self.refresh_keys()
                self.view.clear_key_detail()
            else:
                messagebox.showerror("错误", msg)
    
    def set_ttl(self, key: str):
        """设置过期时间"""
        if not self.redis_model.connected:
            return
        
        ttl = self.view.show_ttl_dialog(key)
        if ttl is not None:
            if ttl == 0:
                # 移除过期时间
                try:
                    self.redis_model.client.persist(key)
                    messagebox.showinfo("成功", "已移除过期时间")
                except Exception as e:
                    messagebox.showerror("错误", f"操作失败: {str(e)}")
            else:
                if self.redis_model.set_key_ttl(key, ttl):
                    messagebox.showinfo("成功", "过期时间已设置")
                else:
                    messagebox.showerror("错误", "设置失败")
            
            # 刷新详情
            self.select_key(key)
    
    def flushdb(self):
        """清空当前数据库"""
        if not self.redis_model.connected:
            return
        
        success, msg = self.redis_model.flushdb()
        if success:
            messagebox.showinfo("成功", msg)
            self.refresh_keys()
        else:
            messagebox.showerror("错误", msg)
    
    def flushall(self):
        """清空所有数据库"""
        if not self.redis_model.connected:
            return
        
        success, msg = self.redis_model.flushall()
        if success:
            messagebox.showinfo("成功", msg)
            self.refresh_keys()
        else:
            messagebox.showerror("错误", msg)
    
    def switch_db(self, db: int):
        """切换数据库"""
        if not self.redis_model.connected:
            return
        
        success, msg = self.redis_model.switch_db(db)
        if success:
            if self.current_connection:
                self.current_connection['db'] = db
            self.refresh_keys()
        else:
            messagebox.showerror("错误", msg)
            # 恢复原来的值
            if self.current_connection:
                self.view.current_db_var.set(str(self.current_connection['db']))
    
    def show_server_info(self):
        """显示服务器信息"""
        if not self.redis_model.connected:
            messagebox.showwarning("提示", "请先连接Redis")
            return
        
        info = self.redis_model.get_server_info()
        if info:
            self.view.show_server_info_dialog(info)
        else:
            messagebox.showerror("错误", "获取服务器信息失败")
    
    def show_client_list(self):
        """显示客户端列表"""
        if not self.redis_model.connected:
            messagebox.showwarning("提示", "请先连接Redis")
            return
        
        from views import ClientListDialog
        dialog = ClientListDialog(self.root, self.redis_model)
        dialog.show()
    
    def get_key_detail_for_copy(self, key: str) -> dict:
        """获取Key详情（用于复制）"""
        if not self.redis_model.connected:
            return {}

        try:
            key_type = self.redis_model.get_key_type(key)
            ttl = self.redis_model.get_key_ttl(key)
            value = self.redis_model.get_key_value(key)
            count = self.redis_model.get_key_count(key, key_type)

            return {
                'type': key_type,
                'ttl': ttl,
                'count': count,
                'value': value
            }
        except Exception as e:
            print(f"获取Key详情失败: {e}")
            return {}

    def export_connections(self):
        """导出连接配置到文件"""
        file_path = filedialog.asksaveasfilename(
            title="导出连接配置",
            defaultextension=".json",
            filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")],
            initialfile="redis_connections.json"
        )
        
        if file_path:
            if self.connection_model.export_connections(file_path):
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
            success, msg = self.connection_model.import_connections(file_path)
            if success:
                self.refresh_connection_list()
                messagebox.showinfo("成功", msg)
            else:
                messagebox.showerror("错误", msg)
