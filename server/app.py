"""企业知识库问答系统后端入口。"""

from flask import Flask
from flask_cors import CORS

from config import Config
from routes.admin import admin_bp
from routes.auth import auth_bp
from routes.chat import chat_bp


def create_app():
    """创建并配置 Flask 应用。"""
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, supports_credentials=True)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(chat_bp, url_prefix="/api/chat")

    @app.route("/")
    def index():
        """提供后端健康检查入口。"""
        return {"message": "EnterpriseQA 后端服务已启动"}

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
