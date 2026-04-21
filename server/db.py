"""数据库连接工具。"""

import pymysql
from pymysql.cursors import DictCursor

from config import Config


def get_connection():
    """创建 MySQL 数据库连接。"""
    return pymysql.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE,
        charset=Config.MYSQL_CHARSET,
        cursorclass=DictCursor,
        autocommit=False,
    )


def query_one(sql, params=None):
    """查询单条记录。"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            return cursor.fetchone()


def query_all(sql, params=None):
    """查询多条记录。"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            return cursor.fetchall()


def execute(sql, params=None):
    """执行新增、修改或删除语句并返回影响行数。"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            rows = cursor.execute(sql, params or ())
        conn.commit()
        return rows


def execute_insert(sql, params=None):
    """执行新增语句并返回自增主键。"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            new_id = cursor.lastrowid
        conn.commit()
        return new_id
