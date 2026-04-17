"""
Redis操作模型 - 封装所有Redis相关操作
"""
import redis
from typing import List, Dict, Optional, Any, Tuple


class RedisModel:
    """Redis操作封装类"""
    
    def __init__(self):
        self.client: Optional[redis.Redis] = None
        self.connected = False
        self.current_db = 0
    
    def connect(self, host: str, port: int, password: str = "", db: int = 0) -> Tuple[bool, str]:
        """连接Redis服务器"""
        try:
            self.client = redis.Redis(
                host=host,
                port=port,
                password=password if password else None,
                db=db,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # 测试连接
            self.client.ping()
            self.connected = True
            self.current_db = db
            return True, "连接成功"
        except redis.ConnectionError as e:
            self.connected = False
            return False, f"连接失败: 无法连接到 {host}:{port}"
        except redis.AuthenticationError as e:
            self.connected = False
            return False, "认证失败: 密码错误"
        except Exception as e:
            self.connected = False
            return False, f"连接异常: {str(e)}"
    
    def disconnect(self):
        """断开连接"""
        if self.client:
            try:
                self.client.close()
            except:
                pass
        self.connected = False
        self.client = None
    
    def switch_db(self, db: int) -> Tuple[bool, str]:
        """切换数据库"""
        if not self.connected:
            return False, "未连接"
        try:
            self.client = redis.Redis(
                host=self.client.connection_pool.connection_kwargs['host'],
                port=self.client.connection_pool.connection_kwargs['port'],
                password=self.client.connection_pool.connection_kwargs.get('password'),
                db=db,
                decode_responses=True
            )
            self.current_db = db
            return True, f"已切换到数据库 {db}"
        except Exception as e:
            return False, f"切换失败: {str(e)}"
    
    def get_keys(self, pattern: str = "*", page: int = 1, page_size: int = 100) -> Tuple[List[str], int]:
        """获取key列表（支持分页和过滤）"""
        if not self.connected:
            return [], 0
        try:
            # 获取所有匹配的key
            all_keys = list(self.client.scan_iter(match=pattern, count=1000))
            total = len(all_keys)
            # 分页
            start = (page - 1) * page_size
            end = start + page_size
            return all_keys[start:end], total
        except Exception as e:
            return [], 0
    
    def get_keys_with_info(self, pattern: str = "*", page: int = 1, page_size: int = 100) -> Tuple[List[Tuple[str, str, int]], int]:
        """获取key列表及类型和TTL信息"""
        if not self.connected:
            return [], 0
        try:
            # 获取所有匹配的key
            all_keys = list(self.client.scan_iter(match=pattern, count=1000))
            total = len(all_keys)
            # 分页
            start = (page - 1) * page_size
            end = start + page_size
            page_keys = all_keys[start:end]
            
            # 获取每个key的类型和TTL
            keys_with_info = []
            for key in page_keys:
                key_type = self.client.type(key)
                ttl = self.client.ttl(key)
                
                # 获取集合类型的大小
                count = ""
                if key_type == 'list':
                    count = self.client.llen(key)
                elif key_type == 'set':
                    count = self.client.scard(key)
                elif key_type == 'zset':
                    count = self.client.zcard(key)
                elif key_type == 'hash':
                    count = self.client.hlen(key)
                
                keys_with_info.append((key, key_type, ttl, count))

            return keys_with_info, total
        except Exception as e:
            return [], 0
    
    def get_key_type(self, key: str) -> Optional[str]:
        """获取key的类型"""
        if not self.connected:
            return None
        try:
            key_type = self.client.type(key)
            return key_type
        except:
            return None
    
    def get_key_value(self, key: str) -> Optional[Any]:
        """获取key的值（根据类型自动处理）"""
        if not self.connected:
            return None
        try:
            key_type = self.client.type(key)
            if key_type == 'string':
                return self.client.get(key)
            elif key_type == 'hash':
                return self.client.hgetall(key)
            elif key_type == 'list':
                return self.client.lrange(key, 0, -1)
            elif key_type == 'set':
                return self.client.smembers(key)
            elif key_type == 'zset':
                return self.client.zrange(key, 0, -1, withscores=True)
            return None
        except:
            return None
    
    def get_key_ttl(self, key: str) -> int:
        """获取key的过期时间"""
        if not self.connected:
            return -2
        try:
            return self.client.ttl(key)
        except:
            return -2
    
    def set_key_ttl(self, key: str, ttl: int) -> bool:
        """设置key的过期时间"""
        if not self.connected:
            return False
        try:
            return self.client.expire(key, ttl)
        except:
            return False
    
    def delete_key(self, key: str) -> bool:
        """删除key"""
        if not self.connected:
            return False
        try:
            return self.client.delete(key) > 0
        except:
            return False
    
    def rename_key(self, old_key: str, new_key: str) -> Tuple[bool, str]:
        """重命名key"""
        if not self.connected:
            return False, "未连接"
        try:
            if self.client.exists(new_key):
                return False, "目标key已存在"
            self.client.rename(old_key, new_key)
            return True, "重命名成功"
        except Exception as e:
            return False, f"重命名失败: {str(e)}"
    
    def add_string_key(self, key: str, value: str, ttl: int = 0) -> Tuple[bool, str]:
        """添加string类型key"""
        if not self.connected:
            return False, "未连接"
        try:
            self.client.set(key, value)
            if ttl > 0:
                self.client.expire(key, ttl)
            return True, "添加成功"
        except Exception as e:
            return False, f"添加失败: {str(e)}"
    
    def add_hash_key(self, key: str, mapping: Dict[str, str], ttl: int = 0) -> Tuple[bool, str]:
        """添加hash类型key"""
        if not self.connected:
            return False, "未连接"
        try:
            self.client.hset(key, mapping=mapping)
            if ttl > 0:
                self.client.expire(key, ttl)
            return True, "添加成功"
        except Exception as e:
            return False, f"添加失败: {str(e)}"
    
    def add_list_key(self, key: str, values: List[str], ttl: int = 0) -> Tuple[bool, str]:
        """添加list类型key"""
        if not self.connected:
            return False, "未连接"
        try:
            self.client.rpush(key, *values)
            if ttl > 0:
                self.client.expire(key, ttl)
            return True, "添加成功"
        except Exception as e:
            return False, f"添加失败: {str(e)}"
    
    def add_set_key(self, key: str, members: List[str], ttl: int = 0) -> Tuple[bool, str]:
        """添加set类型key"""
        if not self.connected:
            return False, "未连接"
        try:
            self.client.sadd(key, *members)
            if ttl > 0:
                self.client.expire(key, ttl)
            return True, "添加成功"
        except Exception as e:
            return False, f"添加失败: {str(e)}"
    
    def add_zset_key(self, key: str, mapping: Dict[str, float], ttl: int = 0) -> Tuple[bool, str]:
        """添加zset类型key"""
        if not self.connected:
            return False, "未连接"
        try:
            self.client.zadd(key, mapping)
            if ttl > 0:
                self.client.expire(key, ttl)
            return True, "添加成功"
        except Exception as e:
            return False, f"添加失败: {str(e)}"
    
    def update_string_value(self, key: str, value: str) -> Tuple[bool, str]:
        """更新string类型值"""
        if not self.connected:
            return False, "未连接"
        try:
            self.client.set(key, value)
            return True, "更新成功"
        except Exception as e:
            return False, f"更新失败: {str(e)}"
    
    def update_hash_value(self, key: str, mapping: Dict[str, str]) -> Tuple[bool, str]:
        """更新hash类型值"""
        if not self.connected:
            return False, "未连接"
        try:
            self.client.delete(key)
            self.client.hset(key, mapping=mapping)
            return True, "更新成功"
        except Exception as e:
            return False, f"更新失败: {str(e)}"
    
    def update_list_value(self, key: str, values: List[str]) -> Tuple[bool, str]:
        """更新list类型值"""
        if not self.connected:
            return False, "未连接"
        try:
            self.client.delete(key)
            self.client.rpush(key, *values)
            return True, "更新成功"
        except Exception as e:
            return False, f"更新失败: {str(e)}"
    
    def update_set_value(self, key: str, members: List[str]) -> Tuple[bool, str]:
        """更新set类型值"""
        if not self.connected:
            return False, "未连接"
        try:
            self.client.delete(key)
            self.client.sadd(key, *members)
            return True, "更新成功"
        except Exception as e:
            return False, f"更新失败: {str(e)}"
    
    def update_zset_value(self, key: str, mapping: Dict[str, float]) -> Tuple[bool, str]:
        """更新zset类型值"""
        if not self.connected:
            return False, "未连接"
        try:
            self.client.delete(key)
            self.client.zadd(key, mapping)
            return True, "更新成功"
        except Exception as e:
            return False, f"更新失败: {str(e)}"
    
    def get_server_info(self) -> Dict[str, str]:
        """获取Redis服务器信息"""
        if not self.connected:
            return {}
        try:
            info = self.client.info()
            result = {}
            # 提取关键信息
            result['redis_version'] = info.get('redis_version', 'N/A')
            result['redis_mode'] = info.get('redis_mode', 'N/A')
            result['tcp_port'] = info.get('tcp_port', 'N/A')
            result['uptime_in_days'] = info.get('uptime_in_days', 'N/A')
            result['connected_clients'] = info.get('connected_clients', 'N/A')
            result['used_memory_human'] = info.get('used_memory_human', 'N/A')
            result['used_memory_peak_human'] = info.get('used_memory_peak_human', 'N/A')
            result['used_memory_rss_human'] = info.get('used_memory_rss_human', 'N/A')
            result['maxmemory_human'] = info.get('maxmemory_human', 'N/A')
            result['mem_fragmentation_ratio'] = info.get('mem_fragmentation_ratio', 'N/A')
            result['total_connections_received'] = info.get('total_connections_received', 'N/A')
            result['total_commands_processed'] = info.get('total_commands_processed', 'N/A')
            result['instantaneous_ops_per_sec'] = info.get('instantaneous_ops_per_sec', 'N/A')
            result['keyspace_hits'] = info.get('keyspace_hits', 'N/A')
            result['keyspace_misses'] = info.get('keyspace_misses', 'N/A')
            result['db_size'] = self.client.dbsize()
            return result
        except Exception as e:
            return {'error': f'获取信息失败: {str(e)}'}
    
    def flushdb(self) -> Tuple[bool, str]:
        """清空当前数据库"""
        if not self.connected:
            return False, "未连接"
        try:
            self.client.flushdb()
            return True, "当前数据库已清空"
        except Exception as e:
            return False, f"清空失败: {str(e)}"
    
    def flushall(self) -> Tuple[bool, str]:
        """清空所有数据库"""
        if not self.connected:
            return False, "未连接"
        try:
            self.client.flushall()
            return True, "所有数据库已清空"
        except Exception as e:
            return False, f"清空失败: {str(e)}"
    
    def db_size(self) -> int:
        """获取当前数据库key数量"""
        if not self.connected:
            return 0
        try:
            return self.client.dbsize()
        except:
            return 0
    
    def get_client_list(self) -> List[Dict[str, str]]:
        """获取当前连接的客户端列表"""
        if not self.connected:
            return []
        try:
            # 使用CLIENT LIST命令获取所有客户端连接
            clients = self.client.client_list()
            return clients
        except Exception as e:
            print(f"获取客户端列表失败: {e}")
            return []
    
    def kill_client(self, addr: str) -> Tuple[bool, str]:
        """断开指定客户端连接"""
        if not self.connected:
            return False, "未连接"
        try:
            # 使用CLIENT KILL命令断开连接
            self.client.execute_command('CLIENT', 'KILL', 'ADDR', addr)
            return True, f"已断开连接: {addr}"
        except Exception as e:
            return False, f"断开失败: {str(e)}"
