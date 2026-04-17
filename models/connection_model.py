"""
连接管理模型 - 负责连接信息的持久化和管理
"""
import json
import os
import platform
from typing import List, Dict, Optional


class ConnectionModel:
    """Redis连接信息管理模型"""

    def __init__(self, config_file: str = "connections.json"):
        # 使用系统用户配置目录，避免更新版本时丢失连接信息
        self.config_dir = self._get_config_dir()
        self.config_file = os.path.join(self.config_dir, config_file)
        self.connections: List[Dict] = []
        self._ensure_config_dir()
        # 尝试从旧位置迁移连接配置
        self._migrate_from_old_location(config_file)
        self.load_connections()

    def _migrate_from_old_location(self, config_file: str):
        """从旧的项目目录迁移连接配置到用户配置目录"""
        # 如果新位置已经有配置文件，不需要迁移
        if os.path.exists(self.config_file):
            return
        
        # 检查旧位置的配置文件（项目根目录）
        old_config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), config_file)
        if os.path.exists(old_config_file):
            try:
                # 读取旧配置
                with open(old_config_file, 'r', encoding='utf-8') as f:
                    old_connections = json.load(f)
                
                # 写入新位置
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(old_connections, f, ensure_ascii=False, indent=2)
                
                print(f"已将连接配置从旧位置迁移到: {self.config_file}")
            except Exception as e:
                print(f"迁移连接配置失败: {e}")

    def _get_config_dir(self) -> str:
        """获取系统用户配置目录"""
        system = platform.system()
        
        if system == "Darwin":  # macOS
            base_dir = os.path.expanduser("~/Library/Application Support")
        elif system == "Linux":
            base_dir = os.path.expanduser("~/.local/share")
        elif system == "Windows":
            base_dir = os.environ.get("APPDATA", os.path.expanduser("~\\AppData\\Local"))
        else:
            # 回退到用户主目录
            base_dir = os.path.expanduser("~")
        
        return os.path.join(base_dir, "RedisVisualManager")

    def _ensure_config_dir(self):
        """确保配置目录存在"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir, exist_ok=True)
    
    def load_connections(self):
        """从文件加载连接配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.connections = json.load(f)
            except Exception as e:
                print(f"加载连接配置失败: {e}")
                self.connections = []
        else:
            self.connections = []
    
    def save_connections(self):
        """保存连接配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.connections, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存连接配置失败: {e}")
            return False
    
    def add_connection(self, alias: str, host: str, port: int, password: str = "", db: int = 0) -> bool:
        """添加新连接"""
        # 检查别名是否已存在
        for conn in self.connections:
            if conn['alias'] == alias:
                return False
        
        connection = {
            'alias': alias,
            'host': host,
            'port': port,
            'password': password,
            'db': db
        }
        self.connections.append(connection)
        return self.save_connections()
    
    def update_connection(self, old_alias: str, alias: str, host: str, port: int, password: str = "", db: int = 0) -> bool:
        """更新连接配置"""
        for conn in self.connections:
            if conn['alias'] == old_alias:
                conn['alias'] = alias
                conn['host'] = host
                conn['port'] = port
                conn['password'] = password
                conn['db'] = db
                return self.save_connections()
        return False
    
    def delete_connection(self, alias: str) -> bool:
        """删除连接配置"""
        self.connections = [c for c in self.connections if c['alias'] != alias]
        return self.save_connections()
    
    def get_connection(self, alias: str) -> Optional[Dict]:
        """获取指定连接配置"""
        for conn in self.connections:
            if conn['alias'] == alias:
                return conn
        return None
    
    def get_all_connections(self) -> List[Dict]:
        """获取所有连接配置"""
        return self.connections.copy()

    def export_connections(self, file_path: str) -> bool:
        """导出连接配置到指定文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.connections, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"导出连接配置失败: {e}")
            return False

    def import_connections(self, file_path: str) -> tuple:
        """从指定文件导入连接配置"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_connections = json.load(f)
            
            # 验证数据格式
            if not isinstance(imported_connections, list):
                return False, "无效的配置文件格式"
            
            for conn in imported_connections:
                if not all(key in conn for key in ['alias', 'host', 'port', 'password', 'db']):
                    return False, "配置文件缺少必要字段"
            
            # 合并连接配置（避免重复）
            existing_aliases = {conn['alias'] for conn in self.connections}
            new_count = 0
            updated_count = 0
            
            for imported_conn in imported_connections:
                if imported_conn['alias'] in existing_aliases:
                    # 更新现有配置
                    self.update_connection(
                        imported_conn['alias'],
                        imported_conn['alias'],
                        imported_conn['host'],
                        imported_conn['port'],
                        imported_conn.get('password', ''),
                        imported_conn['db']
                    )
                    updated_count += 1
                else:
                    # 添加新配置
                    self.add_connection(
                        imported_conn['alias'],
                        imported_conn['host'],
                        imported_conn['port'],
                        imported_conn.get('password', ''),
                        imported_conn['db']
                    )
                    new_count += 1
            
            msg = f"导入成功：新增 {new_count} 个，更新 {updated_count} 个连接配置"
            return True, msg
        except json.JSONDecodeError:
            return False, "无效的JSON文件格式"
        except Exception as e:
            return False, f"导入连接配置失败: {e}"
