"""知识库问答接口。"""

import json

from flask import Blueprint, g, jsonify, request

from db import query_all
from services.rag_service import rag_service
from utils.auth import login_required

chat_bp = Blueprint("chat", __name__)


@chat_bp.post("/ask")
@login_required
def ask():
    """提交问题并返回 RAG 回答。"""
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    if not question:
        return jsonify({"message": "请输入问题"}), 400
    result = rag_service.ask(g.current_user["id"], question)
    return jsonify(result)


@chat_bp.get("/history")
@login_required
def history():
    """查询当前用户的问答历史。"""
    rows = query_all(
        """
        SELECT id, question, answer, references_json, created_at
        FROM qa_record
        WHERE user_id=%s
        ORDER BY id DESC
        LIMIT 50
        """,
        (g.current_user["id"],),
    )
    for row in rows:
        row["references"] = json.loads(row.pop("references_json") or "[]")
    return jsonify({"items": rows})
