"""登录认证接口。"""

from flask import Blueprint, g, jsonify, request

from db import query_one
from utils.auth import create_token, login_required, md5_password

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/login")
def login():
    """用户登录接口。"""
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    if not username or not password:
        return jsonify({"message": "请输入用户名和密码"}), 400

    user = query_one(
        """
        SELECT id, username, password, role, real_name, status
        FROM sys_user
        WHERE username=%s
        """,
        (username,),
    )
    if not user or user["password"] != md5_password(password):
        return jsonify({"message": "用户名或密码错误"}), 400
    if user["status"] != 1:
        return jsonify({"message": "用户已被禁用"}), 403

    safe_user = {
        "id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "real_name": user["real_name"],
    }
    return jsonify({"token": create_token(user), "user": safe_user})


@auth_bp.get("/profile")
@login_required
def profile():
    """获取当前登录用户信息。"""
    return jsonify({"user": g.current_user})
