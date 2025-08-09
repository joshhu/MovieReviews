"""
Flask 應用程式設定檔
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """基礎設定類別"""
    
    # Flask 基礎設定
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # 資料庫設定
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'connect_args': {'check_same_thread': False}
    }
    
    # Session 設定
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    
    # 郵件設定 (Gmail SMTP)
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # TMDb API 設定
    TMDB_API_KEY = os.environ.get('TMDB_API_KEY')
    TMDB_BASE_URL = os.environ.get('TMDB_BASE_URL') or 'https://api.themoviedb.org/3'
    
    # 日誌設定
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'ERROR'
    LOG_FILE = os.environ.get('LOG_FILE') or 'logs/app.log'
    
    # WTF 設定
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # 分頁設定
    MOVIES_PER_PAGE = 20
    REVIEWS_PER_PAGE = 10
    
    # 業務邏輯設定
    MAX_REVIEW_LENGTH = 500
    HERO_CAROUSEL_COUNT = 5
    HERO_AUTOPLAY_INTERVAL = 5000  # 5 秒
    RANKING_UPDATE_HOUR = 2  # 每日 02:00 更新排行榜


class DevelopmentConfig(Config):
    """開發環境設定"""
    DEBUG = True
    SQLALCHEMY_ECHO = False  # 設為 True 可以看到 SQL 查詢


class ProductionConfig(Config):
    """生產環境設定"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    """測試環境設定"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
