# 📰 CloudMind News - 云智新闻系统

<div align="center">

![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat&logo=fastapi)
![Vue.js](https://img.shields.io/badge/Vue.js-3.x-4FC08D?style=flat&logo=vue.js)
![LangGraph](https://img.shields.io/badge/LangGraph-Agent-FF6B6B?style=flat)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector-FFA500?style=flat)
![License](https://img.shields.io/badge/License-MIT-blue.svg)

**基于 FastAPI + LangGraph + ChromaDB 构建的智能化新闻平台**

[功能特性](#-功能特性) • [技术架构](#-技术架构) • [快速开始](#-快速开始) • [API文档](#-api文档) • [部署指南](#-部署指南)

</div>

---

## 📖 项目简介

CloudMind News 是一个仿今日头条的智能新闻系统，采用前后端分离架构。不仅提供传统的新闻浏览、收藏和历史记录功能，还创新性地集成了基于 **LangGraph** 的 AI Agent，支持：

- 🤖 **智能问答**：多轮对话理解上下文
- 🔍 **实时搜索**：联网获取最新时事新闻
- 📚 **知识库检索**：基于向量数据库的本地新闻检索
- 🎯 **智能路由**：自动判断问题类型选择最优策略

---

## ✨ 功能特性

### 核心功能

| 模块 | 功能描述 |
|------|----------|
| 👤 **用户管理** | 注册、登录、JWT认证、个人信息管理 |
| 📰 **新闻浏览** | 分类浏览、分页加载、详情查看、相关新闻推荐 |
| ⭐ **收藏系统** | 添加/取消收藏、收藏列表、状态检查 |
| 📜 **浏览历史** | 自动记录、历史查询、单条删除、清空历史 |
| 🤖 **AI智能问答** | 多轮对话、联网搜索、知识库检索、来源标注 |

### AI Agent 亮点

```
┌─────────────┐
│  User Input │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Router Node │ ──→ 智能分类 (realtime/knowledge/chat)
└──────┬──────┘
       │
       ├─ realtime ──→ 🔍 Search Node (Tavily API)
       │               
       ├─ knowledge ─→ 📚 Retrieve Node (ChromaDB)
       │               
       └─ chat ──────→ 💬 Direct Response
                      │
                      ▼
              🧠 Generate Answer (Qwen LLM)
                      │
                      ▼
                   Output
```

---

## 🛠️ 技术架构

### 后端技术栈

| 类别 | 技术 | 说明 |
|------|------|------|
| **Web框架** | FastAPI | 异步高性能 Web 框架 |
| **ORM** | SQLAlchemy + aiomysql | 异步数据库操作 |
| **向量数据库** | ChromaDB | 持久化向量存储与检索 |
| **缓存** | Redis | 热点数据缓存、会话管理 |
| **AI框架** | LangGraph | Agent 工作流编排 |
| **LLM** | 阿里云百炼 Qwen | 通义千问大语言模型 |
| **Embedding** | text-embedding-v3 | 文本向量化 |
| **搜索** | Tavily API | 实时联网搜索 |
| **认证** | JWT + Bcrypt | Token认证与密码加密 |

### 前端技术栈

| 技术 | 说明 |
|------|------|
| Vue 3 | 渐进式 JavaScript 框架 |
| Vite | 下一代前端构建工具 |
| Pinia | Vue 状态管理 |
| Vue Router | 官方路由管理器 |
| Vant UI | 移动端组件库 |
| Axios | HTTP 客户端 |
| Vue I18n | 国际化支持 |
| Marked | Markdown 渲染 |
| DOMPurify | XSS 防护 |

---

## 📂 项目结构

```
CloudMind_News/
├── agents/                  # AI Agent 核心模块
│   ├── graph.py            # LangGraph 工作流定义
│   ├── nodes.py            # Agent 节点函数
│   ├── state.py            # Agent 状态定义
│   └── tools.py            # Agent 工具集
├── cache/                   # 缓存层封装
│   └── news_cache.py       # 新闻缓存策略
├── config/                  # 配置管理
│   ├── ai_conf.py          # AI 相关配置
│   ├── db_conf.py          # 数据库配置
│   └── cache_conf.py       # Redis 缓存配置
├── crud/                    # 数据访问层
│   ├── chat.py             # AI 会话 CRUD
│   ├── favorite.py         # 收藏操作
│   ├── history.py          # 历史记录操作
│   ├── news.py             # 新闻操作
│   └── users.py            # 用户操作
├── models/                  # SQLAlchemy ORM 模型
│   ├── chat.py             # 会话与消息模型
│   ├── favorite.py         # 收藏模型
│   ├── history.py          # 历史模型
│   ├── news.py             # 新闻模型
│   └── users.py            # 用户模型
├── routers/                 # API 路由
│   ├── ai_chat.py          # AI 聊天接口
│   ├── favorite.py         # 收藏接口
│   ├── history.py          # 历史接口
│   ├── news.py             # 新闻接口
│   └── users.py            # 用户接口
├── schemas/                 # Pydantic 数据验证
│   ├── favorite.py
│   ├── history.py
│   ├── news.py
│   └── users.py
├── services/                # 业务服务层
│   ├── chroma_service.py   # ChromaDB 服务
│   ├── embedding_service.py # Embedding 服务
│   ├── memory_service.py   # Redis 记忆服务
│   ├── summary_service.py  # 摘要服务
│   └── tavily_service.py   # Tavily 搜索服务
├── utils/                   # 工具函数
│   ├── auth.py             # JWT 认证
│   ├── exception.py        # 自定义异常
│   ├── exception_handler.py # 异常处理器
│   ├── response.py         # 统一响应
│   └── security.py         # 安全工具
├── xwzx-news/               # 前端项目 (Vue 3)
│   ├── src/
│   │   ├── components/     # 组件
│   │   ├── views/          # 页面视图
│   │   ├── store/          # Pinia 状态管理
│   │   ├── router/         # 路由配置
│   │   └── i18n/           # 国际化
│   └── package.json
├── main.py                  # 应用入口
├── index_news.py            # 新闻向量化索引脚本
├── create_chat_tables.sql   # 数据库建表脚本
└── .env                     # 环境变量配置
```

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- MySQL 8.0+
- Redis 7.0+

### 后端安装

#### 1. 克隆仓库

```bash
git clone https://github.com/xueran-Breeze/CloudMind_News.git
cd CloudMind_News
```

#### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

#### 3. 安装依赖

```bash
pip install fastapi uvicorn sqlalchemy aiomysql
pip install langgraph chromadb redis
pip install dashscope tavily-python
pip install passlib bcrypt python-jose python-dotenv
pip install pydantic-settings
```

#### 4. 配置环境变量

复制 `.env` 文件并修改配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# 数据库配置
DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/cloudmind_news

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# 阿里云百炼配置
DASHSCOPE_API_KEY=your_api_key_here
DASHSCOPE_MODEL=qwen-plus
DASHSCOPE_EMBEDDING_MODEL=text-embedding-v3

# Tavily 搜索 API
TAVILY_API_KEY=your_tavily_key_here

# ChromaDB 配置
CHROMA_DATA_PATH=./chroma_data
CHROMA_COLLECTION_NAME=news_embeddings

# Agent 配置
CONVERSATION_TTL=86400
MAX_HISTORY_ROUNDS=10
NEWS_CACHE_TTL=600
DETAIL_CACHE_TTL=1800
```

#### 5. 初始化数据库

创建数据库并执行建表脚本：

```bash
mysql -u root -p
CREATE DATABASE cloudmind_news CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE cloudmind_news;
SOURCE create_chat_tables.sql;
```

#### 6. 向量化新闻数据

```bash
python index_news.py
```

#### 7. 启动后端服务

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

访问 API 文档：http://localhost:8000/docs

---

### 前端安装

#### 1. 进入前端目录

```bash
cd xwzx-news
```

#### 2. 安装依赖

```bash
npm install
```

#### 3. 配置 API 地址

编辑 `src/config/api.js`：

```javascript
export const API_BASE_URL = 'http://localhost:8000/api';
```

#### 4. 启动开发服务器

```bash
npm run dev
```

访问前端页面：http://localhost:5173

---

## 📡 API 文档

### 用户接口

| 接口 | 方法 | 说明 | 认证 |
|------|------|------|------|
| `/api/user/register` | POST | 用户注册 | ❌ |
| `/api/user/login` | POST | 用户登录 | ❌ |
| `/api/user/info` | GET | 获取用户信息 | ✅ |
| `/api/user/update` | PUT | 更新用户信息 | ✅ |
| `/api/user/password` | PUT | 修改密码 | ✅ |

### 新闻接口

| 接口 | 方法 | 说明 | 认证 |
|------|------|------|------|
| `/api/news/categories` | GET | 获取分类列表 | ❌ |
| `/api/news/list` | GET | 获取新闻列表 | ❌ |
| `/api/news/detail` | GET | 获取新闻详情 | ❌ |

### 收藏接口

| 接口 | 方法 | 说明 | 认证 |
|------|------|------|------|
| `/api/favorite/check` | GET | 检查收藏状态 | ✅ |
| `/api/favorite/add` | POST | 添加收藏 | ✅ |
| `/api/favorite/remove` | DELETE | 取消收藏 | ✅ |
| `/api/favorite/list` | GET | 获取收藏列表 | ✅ |
| `/api/favorite/clear` | DELETE | 清空收藏 | ✅ |

### 历史接口

| 接口 | 方法 | 说明 | 认证 |
|------|------|------|------|
| `/api/history/add` | POST | 添加浏览记录 | ✅ |
| `/api/history/list` | GET | 获取浏览历史 | ✅ |
| `/api/history/delete/{id}` | DELETE | 删除单条记录 | ✅ |
| `/api/history/clear` | DELETE | 清空历史 | ✅ |

### AI 聊天接口

| 接口 | 方法 | 说明 | 认证 |
|------|------|------|------|
| `/api/ai/chat` | POST | AI 智能问答 | ✅ |
| `/api/ai/chat/new-session` | POST | 创建新会话 | ✅ |
| `/api/ai/chat/sessions` | GET | 获取会话列表 | ✅ |
| `/api/ai/chat/history/{session_id}` | GET | 获取会话历史 | ✅ |
| `/api/ai/chat/history/{session_id}` | DELETE | 删除会话 | ✅ |

### 认证方式

在请求头中添加 Token：

```
Authorization: your_jwt_token_here
```

---

## 🗄️ 数据库设计

### 核心数据表

```sql
-- 用户表
user (id, username, password, nickname, avatar, gender, bio, phone, created_at, updated_at)

-- 用户令牌表
user_token (id, user_id, token, expires_at, created_at)

-- 新闻分类表
news_category (id, name, sort_order, created_at, updated_at)

-- 新闻表
news (id, title, description, content, image, author, category_id, views, publish_time, created_at, updated_at)

-- 收藏表
favorite (id, user_id, news_id, create_time)

-- 浏览历史表
history (id, user_id, news_id, view_time)

-- AI 会话表
chat_session (id, user_id, session_id, title, created_at, updated_at, is_deleted)

-- AI 消息表
chat_message (id, session_id, role, content, sources, question_type, created_at)
```

---

## 🧠 AI Agent 详解

### 工作流程

1. **Router Node（路由节点）**
   - 使用 LLM 分析用户问题
   - 分类为：`realtime`（实时新闻）、`knowledge`（本地知识）、`chat`（闲聊）

2. **Search Node（搜索节点）**
   - 触发条件：`question_type == "realtime"`
   - 调用 Tavily API 进行联网搜索
   - 返回最新的新闻结果

3. **Retrieve Node（检索节点）**
   - 触发条件：`question_type == "knowledge"`
   - 从 ChromaDB 向量数据库检索相似新闻
   - 返回 Top-K 条相关新闻

4. **Context Builder Node（上下文构建）**
   - 整合搜索/检索结果
   - 构建 LLM 可理解的上下文
   - 提取来源信息

5. **Generate Answer Node（答案生成）**
   - 基于上下文和对话历史
   - 使用 Qwen LLM 生成最终回答
   - 自动标注信息来源

### 记忆系统

- **短期记忆**：Redis 存储最近 20 条对话（TTL: 24小时）
- **长期记忆**：MySQL 持久化完整对话历史
- **双层协同**：优先读取 Redis，未命中时从 MySQL 加载

---

## 📦 部署指南

### 生产环境部署

#### 后端部署（使用 Gunicorn + Uvicorn）

```bash
pip install gunicorn

gunicorn main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --access-logfile access.log \
  --error-logfile error.log
```

#### 前端部署

```bash
# 构建生产版本
npm run build

# 部署 dist 目录到 Nginx
cp -r dist/* /var/www/html/
```

#### Nginx 配置

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /var/www/html;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 代理
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Docker 部署（可选）

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_DATABASE: cloudmind_news
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: mysql+aiomysql://root:root_password@mysql:3306/cloudmind_news
      REDIS_HOST: redis
    depends_on:
      - mysql
      - redis

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  mysql_data:
  redis_data:
```

---

## 🔒 安全说明

### 敏感信息管理

⚠️ **重要提示**：`.env` 文件包含敏感的 API Key，请勿上传到公开仓库！

项目已配置 `.gitignore` 自动忽略以下文件：
- `.env` - 环境变量配置
- `chroma_data/` - 向量数据库文件
- `__pycache__/` - Python 缓存文件
- `node_modules/` - Node.js 依赖

### 安全措施

- ✅ 密码使用 Bcrypt 加密存储
- ✅ JWT Token 认证机制（7天有效期）
- ✅ SQL ORM 防止注入攻击
- ✅ CORS 跨域配置
- ✅ 全局异常处理
- ✅ 输入参数 Pydantic 校验

---

## 📊 性能优化

### 缓存策略

| 数据类型 | TTL | 说明 |
|---------|-----|------|
| 新闻详情 | 30分钟 | `news:detail:{news_id}` |
| 新闻列表 | 10分钟 | `news:list:{category}:{page}:{size}` |
| 分类数据 | 2小时 | `news:categories` |
| 用户历史 | 1小时 | `history:list:{user_id}` |
| AI 对话上下文 | 24小时 | `chat:{session_id}` |

### 优化建议

- 使用 Redis 缓存热点数据
- 数据库索引优化（user_id, news_id, session_id）
- 分页查询限制最大 pageSize（100）
- Embedding 向量化结果可缓存
- LLM 调用超时控制
- 对话历史截断（保留最近 5 轮）

---

## 📝 开发规范

### 代码组织

- **分层架构**：Router → CRUD → Model → Schema
- **异步优先**：所有数据库操作使用 async/await
- **统一响应格式**：`{code, message, data}`
- **Pydantic 校验**：严格类型校验

### 命名规范

- 路由前缀：`/api/{module_name}`
- 函数命名：`snake_case`（如 `get_news_list`）
- 类命名：`PascalCase`（如 `VectorDBService`）
- 常量命名：`UPPER_CASE`（如 `REDIS_HOST`）

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 📧 联系方式

- 作者：xueran-Breeze
- Email：2015336143@qq.com
- GitHub：[@xueran-Breeze](https://github.com/xueran-Breeze)

---

## 🙏 致谢

感谢以下开源项目：

- [FastAPI](https://fastapi.tiangolo.com/)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [ChromaDB](https://www.trychroma.com/)
- [Vue.js](https://vuejs.org/)
- [Vant UI](https://vant-ui.github.io/vant/)

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给个 Star 支持一下！**

Made with ❤️ by xueran-Breeze

</div>
