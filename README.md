<<<<<<< HEAD
# EnterpriseQA 企业内部知识库问答系统

这是一个适合入门学习的 LangChain RAG 企业知识库问答 Agent 示例项目。

## 技术栈

- 后端：Python、Flask、PyMySQL、JWT、LangChain
- 前端：Vue3、Vue Router、Axios、ECharts、Vite
- 数据库：MySQL 8，数据库名 `db_enterprise_ga`，端口 `3306`
- 向量数据库：Chroma，本地目录 `server/chroma_db`
- 大模型：Ollama `qwen3:8b`
- 嵌入模型：Ollama `qwen3-embedding:4b`

## 初始化步骤

1. 导入数据库脚本：

```sql
source server/sql/init.sql;
```

2. 安装后端依赖：

```bash
cd server
venv\Scripts\python.exe -m pip install -r requirements.txt
```

3. 启动后端：

```bash
cd server
venv\Scripts\python.exe app.py
```

4. 安装并启动前端：

```bash
cd client
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

5. 可选：将 SQL 测试知识同步到 Chroma：

```bash
cd server
venv\Scripts\python.exe sync_vectors.py
```

## 测试账号

- 管理员：admin / 123456
- 普通用户：user / 123456

## 访问地址

- 前端：http://127.0.0.1:5173/
- 后端：http://127.0.0.1:5000/
=======
# study-haven
用于日常学习记录
>>>>>>> b13e714edb903349ec6eefd07b7dc64b077f8af7
