"""将 MySQL 中未向量化的知识文档同步到 Chroma。"""

from langchain_core.documents import Document

from db import execute, query_all
from services.rag_service import rag_service


def sync_missing_documents():
    """读取 chunk_count 为 0 的文档并写入 Chroma 向量库。"""
    rag_service._ensure_runtime()
    rows = query_all(
        """
        SELECT id, title, source_type, file_name, content
        FROM knowledge_document
        WHERE chunk_count = 0
        ORDER BY id ASC
        """
    )
    for row in rows:
        chunks = rag_service.splitter.split_text(row["content"])
        documents = [
            Document(
                page_content=chunk,
                metadata={
                    "doc_id": row["id"],
                    "title": row["title"],
                    "source_type": row["source_type"],
                    "file_name": row["file_name"] or "",
                    "chunk_index": index,
                },
            )
            for index, chunk in enumerate(chunks)
        ]
        ids = [f"doc_{row['id']}_chunk_{index}" for index in range(len(documents))]
        if documents:
            rag_service.vector_store.add_documents(documents, ids=ids)
        execute("UPDATE knowledge_document SET chunk_count=%s WHERE id=%s", (len(documents), row["id"]))
        print(f"文档 {row['id']} 已同步，片段数：{len(documents)}")


if __name__ == "__main__":
    sync_missing_documents()
