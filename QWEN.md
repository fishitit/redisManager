# Redis Visual Manager - QWEN Context

## 项目概述

**Redis Visual Manager** 是一个基于 Python tkinter 开发的 Redis 图形化管理工具，采用 **MVC（Model-View-Controller）架构模式**。

### 核心功能

- **多 Redis 连接管理**：添加/编辑/删除多个连接配置，本地持久化（JSON 文件）
- **Key-Value 管理**：支持 5 种数据类型（string、hash、list、set、zset）的查看、新增、编辑、删除、重命名、设置过期时间
- **服务器状态查看**：实时展示 Redis 版本、内存使用、客户端连接数等信息
- **客户端连接管理**：查看客户端连接列表，主动断开指定连接
- **数据库操作**：切换数据库（0-15）、清空当前库、清空所有库

### 技术栈

| 组件 | 技术 |
|------|------|
| 编程语言 | Python 3.6+ |
| GUI 框架 | tkinter（内置） |
| Redis 客户端 | redis-py（`redis>=4.0.0`） |
| 架构模式 | MVC |
| 打包工具 | PyInstaller |

---

## 项目结构

```
redisManager/
├── main.py                    # 主程序入口
├── requirements.txt           # 依赖列表
├── connections.json           # 连接配置文件（运行时自动生成）
├── QWEN.md                    # 本文件
├── README.md                  # 使用说明文档
├── 启动说明.md                 # 快速启动指南
├── 软件功能规格说明书.md        # 完整功能规格说明
├── 打包指南.md                 # 打包分发指南
├── build_mac.sh               # macOS 打包脚本
├── build_win.bat              # Windows 打包脚本
├── run.sh                     # 启动脚本
│
├── models/                    # 数据模型层
│   ├── __init__.py
│   ├── connection_model.py    # 连接配置管理（增删改查 + JSON 持久化）
│   └── redis_model.py         # Redis 操作封装（连接、Key 操作、服务器信息等）
│
├── views/                     # 视图层
│   ├── __init__.py
│   ├── main_view.py           # 主界面三栏布局（快捷操作 + Key 列表 + 详情面板）
│   ├── connection_dialog.py   # 连接管理对话框
│   ├── add_key_dialog.py      # 新增/编辑 Key 对话框
│   └── client_list_dialog.py  # 客户端列表对话框
│
├── controllers/               # 控制层
│   ├── __init__.py
│   └── main_controller.py     # 主控制器（绑定视图回调，协调 Model 和 View）
│
└── utils/                     # 工具类（预留）
```

---

## 运行与构建

### 运行程序

```bash
# 安装依赖
pip install redis

# 直接运行
python main.py

# 或使用启动脚本
./run.sh
```

### 打包可执行文件

```bash
# macOS
chmod +x build_mac.sh
./build_mac.sh

# Windows
# 双击执行 build_win.bat
```

打包输出位于 `dist/RedisVisualManager/` 目录。

---

## 架构设计

### MVC 分层

| 层 | 文件 | 职责 |
|----|------|------|
| **Model** | `models/connection_model.py` | 连接配置的增删改查和 JSON 持久化 |
| | `models/redis_model.py` | 封装所有 Redis 操作命令 |
| **View** | `views/main_view.py` | 主界面三栏布局，所有 UI 组件和回调 |
| | `views/connection_dialog.py` | 连接管理对话框 |
| | `views/add_key_dialog.py` | 新增/编辑 Key 对话框 |
| | `views/client_list_dialog.py` | 客户端列表对话框 |
| **Controller** | `controllers/main_controller.py` | 绑定视图回调，协调 Model 和 View |

### 关键类

- **ConnectionModel**：管理 Redis 连接配置，支持 load/save/add/update/delete 操作
- **RedisModel**：封装所有 Redis 操作，包括连接管理、Key 操作（5 种类型）、服务器信息、客户端管理等
- **MainView**：主界面视图，三栏布局（左侧快捷操作、中间 Key 列表、右侧详情面板）
- **Controller**：主控制器，通过回调将 View 事件映射到 Model 操作

### 界面布局

- 顶部状态栏（两行）：连接状态、数据库切换、连接选择、操作按钮
- 主内容区（PanedWindow 三栏，可拖拽调整宽度）：
  - 左侧快捷操作面板：120px
  - 中间 Key 列表面板：550px
  - 右侧 Key 详情面板：550px

---

## 开发约定

### 代码风格

- Python 3.6+ 语法
- 使用类型注解（`typing` 模块）
- 函数/方法使用 docstring 注释
- 遵循 MVC 分层原则，View 和 Model 通过 Controller 交互

### UI 交互

- 使用 `ttk` 组件（clam 主题）
- 危险操作（删除、清空数据库）需要二次确认
- 连接状态使用颜色区分：绿色=已连接，红色=未连接
- Key 列表支持分页、搜索过滤、类型过滤、列排序

### 数据格式

- 连接配置存储为 `connections.json`，UTF-8 编码，格式化（indent=2）
- 不同类型 Key 的输入格式：
  - **string**：直接输入文本
  - **hash**：每行 `field=value`
  - **list**：每行一个元素
  - **set**：每行一个成员
  - **zset**：每行 `member=score`
