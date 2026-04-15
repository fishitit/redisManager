"""
连接管理模型 - 负责连接信息的持久化和管理
"""
import json
import os
from typing import List, Dict, Optional


class ConnectionModel:
    """Redis连接信息管理模型"""
    
    def __init__(self, config_file: str = "connections.json"):
        self.config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), config_file)
        self.connections: List[Dict] = []
        self.load_connections()
    
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
