"""认证与权限工具。"""

import datetime
import functools
import hashlib

import jwt
from flask import g, jsonify, request

from config import Config
from db import query_one


def md5_password(password):
    """将明文密码转换为 MD5 摘要。"""
    return hashlib.md5(password.encode("utf-8")).hexdigest()


def create_token(user):
    """根据用户信息生成 JWT。"""
    payload = {
        "id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=Config.JWT_EXPIRE_HOURS),
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")


def parse_token(token):
    """解析 JWT 并返回载荷。"""
    return jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])


def login_required(view_func):
    """校验登录态的路由装饰器。"""
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        token = auth_header.replace("Bearer ", "", 1).strip()
        if not token:
            return jsonify({"message": "请先登录"}), 401

        try:
            payload = parse_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "登录已过期，请重新登录"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "无效的登录凭证"}), 401

        user = query_one(
            "SELECT id, username, role, real_name, status FROM sys_user WHERE id=%s",
            (payload["id"],),
        )
        if not user or user["status"] != 1:
            return jsonify({"message": "用户不存在或已被禁用"}), 401

        g.current_user = user
        return view_func(*args, **kwargs)

    return wrapper


def admin_required(view_func):
    """校验管理员角色的路由装饰器。"""
    @functools.wraps(view_func)
    @login_required
    def wrapper(*args, **kwargs):
        if g.current_user["role"] != "admin":
            return jsonify({"message": "需要管理员权限"}), 403
        return view_func(*args, **kwargs)

    return wrapper
