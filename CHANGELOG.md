# 更新日志

## v1.1.0 (2026-04-17)

### 🎉 新功能

#### 连接配置持久化优化
- 连接信息保存到系统用户配置目录，更新版本不再丢失
  - macOS: `~/Library/Application Support/RedisVisualManager/`
  - Linux: `~/.local/share/RedisVisualManager/`
  - Windows: `%APPDATA%/RedisVisualManager/`
- 首次启动自动从旧项目目录迁移连接配置到新位置

#### 连接配置导入/导出
- 在快捷操作面板添加导入导出按钮
- 在连接管理对话框添加导入导出按钮
- 支持导出为 JSON 格式，方便备份和跨设备迁移

#### Key 列表显示增强
- 新增"个数"列，显示集合类型 Key 的元素大小
  - list: 显示元素个数 (LLEN)
  - set: 显示元素个数 (SCARD)
  - zset: 显示元素个数 (ZCARD)
  - hash: 显示字段个数 (HLEN)
- 支持按个数列排序

#### Key 详情显示增强
- 详情区域新增"个数"字段显示
- 勾选"自动刷新"时，每秒同步更新个数信息

#### 连接管理对话框增强
- Treeview 支持多选 (Ctrl/Shift + 点击)
- 支持批量删除多个连接配置
- 根据选中数量显示不同的确认提示信息
- 删除完成后显示成功/失败统计

### 🐛 修复

- 修复连接管理对话框新增按钮后显示不全的问题（高度 500→600）
- 修复缺少导入导出回调方法导致的 AttributeError

### 🔧 项目优化

- 添加 `.gitignore` 文件，忽略打包产物和临时文件
  - 忽略 `dist/` 和 `build/` 目录
  - 忽略 `__pycache__/` 和 `*.pyc` 文件
  - 忽略 `connections.json` 用户配置（包含密码）
  - 忽略 `.DS_Store` macOS 系统文件
  - 忽略 IDE 配置文件
- 从 git 跟踪中移除 890 个打包产物文件
- 现在 git 提交只包含源代码文件

### 📝 代码变更

- `models/connection_model.py`: 配置保存到系统目录，新增导入导出方法
- `views/connection_dialog.py`: 支持多选批量删除，增加对话框高度
- `views/main_view.py`: 新增个数列和详情个数显示，添加导入导出回调
- `models/redis_model.py`: 新增 get_key_count 方法，get_keys_with_info 返回个数信息
- `controllers/main_controller.py`: 实现导入导出功能，详情获取增加个数

---

## v1.0.0 (2026-04-15)

### 初始版本

- 多 Redis 连接管理（添加/保存/删除/切换）
- Key-Value 管理（支持 string/hash/list/set/zset 五种类型）
- Redis 服务状态查看
- 数据库操作（切换/清空）
- 连接配置持久化
- 分页浏览
- Key 搜索和类型过滤
- TTL 管理
- 批量删除
- Key 重命名
- 客户端列表查看
