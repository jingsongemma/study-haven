"""LangChain RAG 问答服务。"""

import json
import os

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import Config
from db import execute, execute_insert, query_one


class RagService:
    """封装知识入库、向量检索和大模型问答能力。"""

    def __init__(self):
        """创建服务实例，模型和向量库在首次使用时懒加载。"""
        self.embeddings = None
        self.llm = None
        self.splitter = None
        self.vector_store = None

    def _ensure_runtime(self):
        """按需初始化百炼模型、文本切分器和 Chroma 向量库。"""
        if self.vector_store:
            return
        if not Config.BAILIAN_API_KEY:
            raise RuntimeError("请先在 server/.env 中配置 DASHSCOPE_API_KEY 或 BAILIAN_API_KEY")
        os.makedirs(Config.CHROMA_DIR, exist_ok=True)
        self.embeddings = OpenAIEmbeddings(
            model=Config.BAILIAN_EMBEDDING_MODEL,
            api_key=Config.BAILIAN_API_KEY,
            base_url=Config.BAILIAN_BASE_URL,
            dimensions=Config.BAILIAN_EMBEDDING_DIMENSIONS,
            check_embedding_ctx_length=False,
        )
        self.llm = ChatOpenAI(
            model=Config.BAILIAN_LLM_MODEL,
            api_key=Config.BAILIAN_API_KEY,
            base_url=Config.BAILIAN_BASE_URL,
            temperature=0.2,
        )
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
        self.vector_store = Chroma(
            collection_name=Config.CHROMA_COLLECTION,
            embedding_function=self.embeddings,
            persist_directory=Config.CHROMA_DIR,
        )

    def add_document(self, title, content, source_type, file_name, user_id):
        """保存知识文档并写入 Chroma 向量库。"""
        self._ensure_runtime()
        doc_id = execute_insert(
            """
            INSERT INTO knowledge_document(title, source_type, file_name, content, chunk_count, created_by)
            VALUES(%s, %s, %s, %s, %s, %s)
            """,
            (title, source_type, file_name, content, 0, user_id),
        )
        chunks = self.splitter.split_text(content)
        documents = [
            Document(
                page_content=chunk,
                metadata={
                    "doc_id": doc_id,
                    "title": title,
                    "source_type": source_type,
                    "file_name": file_name or "",
                    "chunk_index": index,
                },
            )
            for index, chunk in enumerate(chunks)
        ]
        ids = [f"doc_{doc_id}_chunk_{index}" for index in range(len(documents))]
        if documents:
            self.vector_store.add_documents(documents, ids=ids)

        execute(
            "UPDATE knowledge_document SET chunk_count=%s WHERE id=%s",
            (len(documents), doc_id),
        )
        return doc_id, len(documents)

    def delete_document(self, doc_id):
        """删除知识文档及其对应向量片段。"""
        self._ensure_runtime()
        document = query_one(
            "SELECT id, chunk_count FROM knowledge_document WHERE id=%s",
            (doc_id,),
        )
        if not document:
            return False

        ids = [f"doc_{doc_id}_chunk_{index}" for index in range(document["chunk_count"])]
        if ids:
            self.vector_store.delete(ids=ids)
        execute("DELETE FROM knowledge_document WHERE id=%s", (doc_id,))
        return True

    def ask(self, user_id, question):
        """执行 RAG 检索增强问答并记录历史。"""
        self._ensure_runtime()
        docs = self.vector_store.similarity_search(question, k=4)
        context = "\n\n".join(
            [f"资料标题：{doc.metadata.get('title')}\n内容：{doc.page_content}" for doc in docs]
        )
        prompt = f"""
你是企业内部知识库问答助手。请只根据给定资料回答问题。
如果资料中没有答案，请明确说明“知识库中暂未找到相关信息”。

【知识库资料】
{context or "暂无相关资料"}

【用户问题】
{question}
"""
        response = self.llm.invoke(prompt)
        answer = response.content if hasattr(response, "content") else str(response)
        references = [
            {
                "doc_id": doc.metadata.get("doc_id"),
                "title": doc.metadata.get("title"),
                "source_type": doc.metadata.get("source_type"),
                "file_name": doc.metadata.get("file_name"),
                "chunk_index": doc.metadata.get("chunk_index"),
            }
            for doc in docs
        ]
        record_id = execute_insert(
            """
            INSERT INTO qa_record(user_id, question, answer, references_json)
            VALUES(%s, %s, %s, %s)
            """,
            (user_id, question, answer, json.dumps(references, ensure_ascii=False)),
        )
        return {"record_id": record_id, "answer": answer, "references": references}


rag_service = RagService()
