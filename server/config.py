"""项目配置文件。"""

import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """集中维护数据库、JWT、百炼和 Chroma 配置。"""

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SECRET_KEY = os.getenv("SECRET_KEY", "enterprise-qa-dev-secret")
    JWT_SECRET = os.getenv("JWT_SECRET", "enterprise-qa-jwt-secret")
    JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "24"))

    MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "123456")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "db_enterprise_ga")
    MYSQL_CHARSET = "utf8mb4"

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    CHROMA_DIR = os.getenv("CHROMA_DIR", os.path.join(BASE_DIR, "chroma_db"))
    CHROMA_COLLECTION = "enterprise_knowledge"

    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "bailian")
    BAILIAN_API_KEY = os.getenv("DASHSCOPE_API_KEY", os.getenv("BAILIAN_API_KEY", ""))
    BAILIAN_BASE_URL = os.getenv(
        "BAILIAN_BASE_URL",
        "https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    BAILIAN_LLM_MODEL = os.getenv("BAILIAN_LLM_MODEL", "qwen-plus")
    BAILIAN_EMBEDDING_MODEL = os.getenv("BAILIAN_EMBEDDING_MODEL", "text-embedding-v4")
    BAILIAN_EMBEDDING_DIMENSIONS = int(os.getenv("BAILIAN_EMBEDDING_DIMENSIONS", "1024"))
