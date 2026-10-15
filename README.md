# 校园项目 - 技术支持部开发项目

本仓库包含两个子项目：

| 项目 | 说明 |
|------|------|
| `counselor-ai-agent` | 辅导员AI智能体 — 基于RAG的知识问答系统 |
| `competition-info-system` | 比赛查询系统 — 竞赛信息发布与管理网页 |

## 技术栈（两项目共用）

- **后端**：Python 3.11 + FastAPI + SQLAlchemy + Pydantic
- **数据库**：PostgreSQL（开发环境可用 SQLite 替代）
- **AI 项目专用**：LangChain + Chroma（向量数据库）
- **前端（比赛查询系统）**：Vue 3 + Vite + Element Plus

## 快速开始

```bash
# 克隆仓库
git clone <repo-url> && cd campus-projects

# 安装依赖（每个项目独立虚拟环境）
cd counselor-ai-agent/backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
cd competition-info-system/backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
cd competition-info-system/frontend && npm install

# 启动开发服务器
# AI项目后端: cd counselor-ai-agent/backend && uvicorn app.main:app --reload
# 比赛系统后端: cd competition-info-system/backend && uvicorn app.main:app --reload
# 比赛系统前端: cd competition-info-system/frontend && npm run dev
```
