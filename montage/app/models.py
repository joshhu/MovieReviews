"""
SQLAlchemy 資料模型
"""
from datetime import datetime
from typing import List, Optional
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import bcrypt
from app import db


class User(UserMixin, db.Model):
    """使用者模型"""
    
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    email_confirmed = db.Column(db.Boolean, default=False, nullable=False)
    confirmation_token = db.Column(db.String(255), nullable=True)
    
    # 關聯
    reviews = db.relationship('Review', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, email: str, password: str, display_name: str) -> None:
        """
        初始化使用者
        
        Args:
            email: 電子郵件
            password: 密碼（明文）
            display_name: 顯示名稱
        """
        self.email = email
        self.set_password(password)
        self.display_name = display_name
    
    def set_password(self, password: str) -> None:
        """
        設定密碼（bcrypt 雜湊）
        
        Args:
            password: 明文密碼
        """
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """
        驗證密碼
        
        Args:
            password: 明文密碼
            
        Returns:
            密碼是否正確
        """
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def get_id(self) -> str:
        """Flask-Login 需要的方法"""
        return str(self.user_id)
    
    def get_review_count(self) -> int:
        """取得使用者評論數量"""
        return self.reviews.count()
    
    def has_reviewed_movie(self, movie_id: int) -> bool:
        """
        檢查使用者是否已評論該電影
        
        Args:
            movie_id: 電影 ID
            
        Returns:
            是否已評論
        """
        return self.reviews.filter_by(movie_id=movie_id).first() is not None
    
    def __repr__(self) -> str:
        return f'<User {self.email}>'


class Movie(db.Model):
    """電影模型"""
    
    __tablename__ = 'movies'
    
    movie_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    release_year = db.Column(db.Integer, nullable=True, index=True)
    avg_rating = db.Column(db.Float, default=0.0, nullable=False)
    poster_url = db.Column(db.String(500), nullable=True)
    genre_ids = db.Column(db.Text, nullable=True)  # JSON 字串格式
    runtime = db.Column(db.Integer, nullable=True)
    tagline = db.Column(db.Text, nullable=True)
    overview = db.Column(db.Text, nullable=True)
    vote_average = db.Column(db.Float, nullable=True)  # TMDb 評分
    tmdb_id = db.Column(db.Integer, unique=True, nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # 關聯
    reviews = db.relationship('Review', backref='movie', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, title: str, release_year: Optional[int] = None, **kwargs) -> None:
        """
        初始化電影
        
        Args:
            title: 電影標題
            release_year: 上映年份
            **kwargs: 其他屬性
        """
        self.title = title
        self.release_year = release_year
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def get_review_count(self) -> int:
        """取得電影評論數量"""
        return self.reviews.count()
    
    def calculate_avg_rating(self) -> None:
        """重新計算平均評分"""
        reviews = self.reviews.all()
        if reviews:
            total_rating = sum(review.rating for review in reviews)
            self.avg_rating = round(total_rating / len(reviews), 2)
        else:
            self.avg_rating = 0.0
        db.session.commit()
    
    def get_recent_reviews(self, limit: int = 5) -> List['Review']:
        """
        取得最近的評論
        
        Args:
            limit: 限制數量
            
        Returns:
            評論列表
        """
        return self.reviews.order_by(Review.created_at.desc()).limit(limit).all()
    
    def get_genre_list(self) -> List[str]:
        """
        取得類型列表
        
        Returns:
            類型名稱列表
        """
        if not self.genre_ids:
            return []
        
        # 這裡應該根據 TMDb 的 genre mapping 來轉換
        # 暫時返回空列表，後續實作時補上
        return []
    
    def __repr__(self) -> str:
        return f'<Movie {self.title} ({self.release_year})>'


class Review(db.Model):
    """評論模型"""
    
    __tablename__ = 'reviews'
    
    review_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False, index=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id'), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 星
    comment_text = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 建立複合唯一索引，確保一個使用者對一部電影只能評論一次
    __table_args__ = (
        db.UniqueConstraint('user_id', 'movie_id', name='unique_user_movie_review'),
    )
    
    def __init__(self, user_id: int, movie_id: int, rating: int, comment_text: Optional[str] = None) -> None:
        """
        初始化評論
        
        Args:
            user_id: 使用者 ID
            movie_id: 電影 ID
            rating: 評分 (1-5)
            comment_text: 評論文字
        """
        self.user_id = user_id
        self.movie_id = movie_id
        self.rating = rating
        self.comment_text = comment_text
    
    def validate_rating(self) -> bool:
        """
        驗證評分範圍
        
        Returns:
            評分是否有效
        """
        return 1 <= self.rating <= 5
    
    def validate_comment_length(self, max_length: int = 500) -> bool:
        """
        驗證評論長度
        
        Args:
            max_length: 最大長度
            
        Returns:
            評論長度是否有效
        """
        if not self.comment_text:
            return True
        return len(self.comment_text) <= max_length
    
    def is_recent(self, days: int = 7) -> bool:
        """
        檢查是否為最近的評論
        
        Args:
            days: 天數
            
        Returns:
            是否為最近評論
        """
        from datetime import timedelta
        return (datetime.utcnow() - self.created_at) <= timedelta(days=days)
    
    def __repr__(self) -> str:
        return f'<Review User:{self.user_id} Movie:{self.movie_id} Rating:{self.rating}>'
