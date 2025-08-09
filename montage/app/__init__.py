"""
Flask 應用程式工廠
"""
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_admin import Admin
from flask_wtf.csrf import CSRFProtect
from config import config

# 初始化擴展
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
flask_admin = Admin()
csrf = CSRFProtect()


def create_app(config_name: str = None) -> Flask:
    """
    Flask 應用程式工廠函數
    
    Args:
        config_name: 設定名稱 ('development', 'production', 'testing')
        
    Returns:
        Flask 應用程式實例
    """
    app = Flask(__name__)
    
    # 載入設定
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # 初始化擴展
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    flask_admin.init_app(app)
    csrf.init_app(app)
    
    # 設定 Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '請先登入以訪問此頁面。'
    login_manager.login_message_category = 'info'
    
    # 設定 Flask-Admin
    flask_admin.name = '蒙太奇之愛 管理後台'
    flask_admin.template_mode = 'bootstrap4'
    
    # 設定日誌
    setup_logging(app)
    
    # 註冊 Blueprint
    from app.routes import main
    from app.auth import bp as auth_bp
    
    app.register_blueprint(main)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # 註冊 Flask-Admin 視圖
    from app.admin import register_admin_views
    register_admin_views(flask_admin, db)
    
    # 註冊用戶載入器
    from app.models import User
    
    @login_manager.user_loader
    def load_user(user_id: str) -> User:
        return User.query.get(int(user_id))
    
    # 建立資料庫表格
    with app.app_context():
        db.create_all()
    
    # 啟動排程器
    if not app.config.get('TESTING'):
        from app.scheduler import start_scheduler
        start_scheduler(app)
    
    return app


def setup_logging(app: Flask) -> None:
    """
    設定應用程式日誌
    
    Args:
        app: Flask 應用程式實例
    """
    if not app.debug and not app.testing:
        # 建立日誌目錄
        log_dir = os.path.dirname(app.config['LOG_FILE'])
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 設定 TimedRotatingFileHandler
        file_handler = TimedRotatingFileHandler(
            app.config['LOG_FILE'],
            when='midnight',
            interval=1,
            backupCount=7,
            encoding='utf-8'
        )
        
        # 設定日誌格式
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s %(name)s: %(message)s [%(pathname)s:%(lineno)d]'
        )
        file_handler.setFormatter(formatter)
        
        # 設定日誌級別
        log_level = getattr(logging, app.config.get('LOG_LEVEL', 'ERROR'))
        file_handler.setLevel(log_level)
        
        # 添加到應用程式日誌記錄器
        app.logger.addHandler(file_handler)
        app.logger.setLevel(log_level)
        
        app.logger.info('蒙太奇之愛 啟動完成')
