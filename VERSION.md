# 版本更新日志

## v1.1.0 - 2026-04-15

### 🐛 Bug 修复

- **修复打包后运行提示"库不存在"的问题**
  - 原因：PyInstaller 无法自动检测动态导入的模块
  - 解决：在打包脚本中添加 `--hidden-import` 参数，显式声明所有依赖模块

### 🔧 打包脚本优化

- **`build_win.bat`** - Windows 打包脚本
  - 新增 `--hidden-import` 参数：
    - `redis`, `redis.client`, `redis.connection`
    - `tkinter`, `tkinter.ttk`, `tkinter.messagebox`, `tkinter.filedialog`
    - `models.connection_model`, `models.redis_model`
    - `views.main_view`, `views.connection_dialog`, `views.add_key_dialog`, `views.client_list_dialog`
    - `controllers.main_controller`
  - 新增 `--noconfirm` 参数，避免打包时交互确认

- **`build_mac.sh`** - macOS 打包脚本
  - 同步新增上述所有 `--hidden-import` 参数
  - 新增 `--noconfirm` 参数

### 📝 文档更新

- **`README.md`**
  - 更新项目结构，补充完整的文件列表
  - 新增"打包可执行文件"章节

- **`打包指南.md`**
  - 更新所有手动打包命令，补充 `--hidden-import` 参数
  - 更新"提示找不到模块"常见问题解答，详细说明 hidden-import 的必要性
  - 更新单文件模式和添加图标章节的打包命令

- **`启动说明.md`**
  - 更新项目结构，补充打包脚本和新增文档

- **`QWEN.md`**
  - 新增项目上下文文件，记录项目架构、技术栈、开发约定

### 📦 新增文件

- **`VERSION.md`** - 版本更新日志（本文件）

---

## v1.0.0 - 初始版本

### ✨ 功能特性

- 多 Redis 连接管理（添加/编辑/删除/切换）
- Key-Value 管理（支持 string/hash/list/set/zset 五种数据类型）
- Key 列表展示（支持分页、搜索过滤、类型过滤、列排序）
- Key 详情查看与编辑
- Redis 服务器信息查看
- 客户端连接列表查看与断开
- 数据库操作（切换/清空当前库/清空所有库）
- JSON 校验与格式化
- 右键菜单（复制 Key/Value/完整信息）

### 🏗️ 技术架构

- **GUI 框架**：tkinter（Python 内置）
- **Redis 客户端**：redis-py
- **架构模式**：MVC（Model-View-Controller）
- **Python 版本**：3.6+

---
