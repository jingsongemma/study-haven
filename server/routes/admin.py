"""管理员后台接口。"""

import os
import time

from flask import Blueprint, g, jsonify, request
from werkzeug.utils import secure_filename

from config import Config
from db import execute, query_all, query_one
from services.rag_service import rag_service
from utils.auth import admin_required, md5_password
from utils.file_loader import FileLoader

admin_bp = Blueprint("admin", __name__)


@admin_bp.get("/stats")
@admin_required
def stats():
    """获取后台首页统计数据。"""
    user_count = query_one("SELECT COUNT(*) AS total FROM sys_user")["total"]
    doc_count = query_one("SELECT COUNT(*) AS total FROM knowledge_document")["total"]
    qa_count = query_one("SELECT COUNT(*) AS total FROM qa_record")["total"]
    role_rows = query_all("SELECT role, COUNT(*) AS total FROM sys_user GROUP BY role")
    daily_rows = query_all(
        """
        SELECT DATE(created_at) AS day, COUNT(*) AS total
        FROM qa_record
        GROUP BY DATE(created_at)
        ORDER BY day DESC
        LIMIT 7
        """
    )
    return jsonify({
        "cards": {"users": user_count, "documents": doc_count, "qa": qa_count},
        "roles": role_rows,
        "daily_qa": list(reversed(daily_rows)),
    })


@admin_bp.get("/users")
@admin_required
def list_users():
    """查询用户列表。"""
    rows = query_all(
        """
        SELECT id, username, role, real_name, status, created_at
        FROM sys_user
        ORDER BY id DESC
        """
    )
    return jsonify({"items": rows})


@admin_bp.post("/users")
@admin_required
def create_user():
    """创建用户，默认密码为 123456。"""
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    real_name = (data.get("real_name") or username).strip()
    role = data.get("role") or "user"
    if not username or role not in ["admin", "user"]:
        return jsonify({"message": "用户信息不完整"}), 400
    exists = query_one("SELECT id FROM sys_user WHERE username=%s", (username,))
    if exists:
        return jsonify({"message": "用户名已存在"}), 400
    execute(
        """
        INSERT INTO sys_user(username, password, role, real_name, status)
        VALUES(%s, %s, %s, %s, 1)
        """,
        (username, md5_password("123456"), role, real_name),
    )
    return jsonify({"message": "创建成功"})


@admin_bp.put("/users/<int:user_id>")
@admin_required
def update_user(user_id):
    """更新用户角色、姓名和状态。"""
    data = request.get_json(silent=True) or {}
    role = data.get("role") or "user"
    real_name = (data.get("real_name") or "").strip()
    status = int(data.get("status", 1))
    if role not in ["admin", "user"] or status not in [0, 1]:
        return jsonify({"message": "用户参数不合法"}), 400
    execute(
        "UPDATE sys_user SET role=%s, real_name=%s, status=%s WHERE id=%s",
        (role, real_name, status, user_id),
    )
    return jsonify({"message": "更新成功"})


@admin_bp.delete("/users/<int:user_id>")
@admin_required
def delete_user(user_id):
    """删除用户，禁止删除当前登录账号。"""
    if g.current_user["id"] == user_id:
        return jsonify({"message": "不能删除当前登录账号"}), 400
    execute("DELETE FROM sys_user WHERE id=%s", (user_id,))
    return jsonify({"message": "删除成功"})


@admin_bp.get("/documents")
@admin_required
def list_documents():
    """查询知识文档列表。"""
    rows = query_all(
        """
        SELECT d.id, d.title, d.source_type, d.file_name, d.chunk_count, d.created_at,
               u.real_name AS creator
        FROM knowledge_document d
        LEFT JOIN sys_user u ON d.created_by = u.id
        ORDER BY d.id DESC
        """
    )
    return jsonify({"items": rows})


@admin_bp.get("/qa-records")
@admin_required
def list_qa_records():
    """查询全部用户的问答历史记录。"""
    rows = query_all(
        """
        SELECT r.id, r.question, r.answer, r.references_json, r.created_at,
               u.username, u.real_name
        FROM qa_record r
        LEFT JOIN sys_user u ON r.user_id = u.id
        ORDER BY r.id DESC
        LIMIT 200
        """
    )
    return jsonify({"items": rows})


@admin_bp.post("/documents/text")
@admin_required
def create_text_document():
    """通过文本粘贴新增知识文档。"""
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    content = (data.get("content") or "").strip()
    if not title or not content:
        return jsonify({"message": "标题和正文不能为空"}), 400
    doc_id, chunk_count = rag_service.add_document(title, content, "text", "", g.current_user["id"])
    return jsonify({"message": "知识入库成功", "id": doc_id, "chunk_count": chunk_count})


@admin_bp.post("/documents/upload")
@admin_required
def upload_document():
    """通过文件上传新增知识文档。"""
    file = request.files.get("file")
    title = (request.form.get("title") or "").strip()
    if not file:
        return jsonify({"message": "请选择上传文件"}), 400
    filename = secure_filename(file.filename or "")
    if not filename or filename.rsplit(".", 1)[-1].lower() not in ["txt", "pdf", "docx"]:
        return jsonify({"message": "仅支持 txt、pdf、docx 文件"}), 400

    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    saved_name = f"{int(time.time())}_{filename}"
    file_path = os.path.join(Config.UPLOAD_FOLDER, saved_name)
    file.save(file_path)
    content = FileLoader.load_text(file_path, filename).strip()
    if not content:
        return jsonify({"message": "文件未解析出有效文本"}), 400
    doc_id, chunk_count = rag_service.add_document(
        title or filename,
        content,
        "file",
        filename,
        g.current_user["id"],
    )
    return jsonify({"message": "文件知识入库成功", "id": doc_id, "chunk_count": chunk_count})


@admin_bp.delete("/documents/<int:doc_id>")
@admin_required
def delete_document(doc_id):
    """删除知识文档和对应向量数据。"""
    deleted = rag_service.delete_document(doc_id)
    if not deleted:
        return jsonify({"message": "知识文档不存在"}), 404
    return jsonify({"message": "删除成功"})
