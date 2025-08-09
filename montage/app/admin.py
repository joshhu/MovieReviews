"""
Flask-Admin 管理後台
"""
from flask import redirect, url_for, request, flash
from flask_login import current_user
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import Select2Field
from wtforms import SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange
from app.models import User, Movie, Review


class AdminIndexView(AdminIndexView):
    """管理後台首頁視圖"""
    
    @expose('/')
    def index(self):
        # 檢查管理員權限
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login', next=request.url))
        
        # 這裡可以檢查使用者是否為管理員
        # 暫時允許所有已登入用戶訪問
        
        # 統計資訊
        from app import db
        from sqlalchemy import func
        
        total_users = User.query.count()
        total_movies = Movie.query.count()
        total_reviews = Review.query.count()
        
        # 最新註冊用戶
        recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
        
        # 最新評論
        recent_reviews = Review.query.join(Movie).join(User)\
            .order_by(Review.created_at.desc()).limit(10).all()
        
        # 熱門電影
        popular_movies = db.session.query(Movie)\
            .join(Review)\
            .group_by(Movie.movie_id)\
            .order_by(func.count(Review.review_id).desc())\
            .limit(10).all()
        
        return self.render(
            'admin/dashboard.html',
            total_users=total_users,
            total_movies=total_movies,
            total_reviews=total_reviews,
            recent_users=recent_users,
            recent_reviews=recent_reviews,
            popular_movies=popular_movies
        )
    
    def is_accessible(self):
        """檢查是否有訪問權限"""
        return current_user.is_authenticated
    
    def inaccessible_callback(self, name, **kwargs):
        """無權限時的回調"""
        return redirect(url_for('auth.login', next=request.url))


class UserModelView(ModelView):
    """使用者管理視圖"""
    
    # 列表頁面設定
    column_list = ['user_id', 'email', 'display_name', 'email_confirmed', 'created_at']
    column_searchable_list = ['email', 'display_name']
    column_filters = ['email_confirmed', 'is_active', 'created_at']
    column_sortable_list = ['user_id', 'email', 'display_name', 'created_at']
    column_default_sort = ('created_at', True)
    
    # 編輯頁面設定
    form_excluded_columns = ['password_hash', 'confirmation_token', 'reviews']
    form_widget_args = {
        'email': {'readonly': True},
        'created_at': {'readonly': True}
    }
    
    # 自訂欄位標籤
    column_labels = {
        'user_id': 'ID',
        'email': '電子郵件',
        'display_name': '顯示名稱',
        'email_confirmed': '信箱已確認',
        'is_active': '帳戶啟用',
        'created_at': '註冊時間'
    }
    
    def is_accessible(self):
        return current_user.is_authenticated
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login', next=request.url))


class MovieModelView(ModelView):
    """電影管理視圖"""
    
    # 列表頁面設定
    column_list = ['movie_id', 'title', 'release_year', 'avg_rating', 'created_at']
    column_searchable_list = ['title', 'overview', 'tagline']
    column_filters = ['release_year', 'avg_rating', 'created_at']
    column_sortable_list = ['movie_id', 'title', 'release_year', 'avg_rating', 'created_at']
    column_default_sort = ('created_at', True)
    
    # 編輯頁面設定
    form_excluded_columns = ['reviews', 'avg_rating', 'created_at']
    form_widget_args = {
        'tmdb_id': {'readonly': True},
        'avg_rating': {'readonly': True}
    }
    
    # 自訂表單欄位
    form_overrides = {
        'overview': TextAreaField,
        'tagline': TextAreaField,
        'genre_ids': TextAreaField
    }
    
    form_args = {
        'title': {
            'validators': [DataRequired(), Length(max=255)]
        },
        'release_year': {
            'validators': [NumberRange(min=1900, max=2030)]
        },
        'overview': {
            'validators': [Length(max=1000)]
        },
        'runtime': {
            'validators': [NumberRange(min=1, max=600)]
        }
    }
    
    # 自訂欄位標籤
    column_labels = {
        'movie_id': 'ID',
        'title': '電影標題',
        'release_year': '上映年份',
        'avg_rating': '平均評分',
        'poster_url': '海報連結',
        'genre_ids': '類型 ID',
        'runtime': '片長（分鐘）',
        'tagline': '標語',
        'overview': '簡介',
        'vote_average': 'TMDb 評分',
        'tmdb_id': 'TMDb ID',
        'created_at': '建立時間'
    }
    
    def is_accessible(self):
        return current_user.is_authenticated
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login', next=request.url))


class ReviewModelView(ModelView):
    """評論管理視圖"""
    
    # 列表頁面設定
    column_list = ['review_id', 'user.display_name', 'movie.title', 'rating', 'created_at']
    column_searchable_list = ['comment_text']
    column_filters = ['rating', 'created_at', 'updated_at']
    column_sortable_list = ['review_id', 'rating', 'created_at', 'updated_at']
    column_default_sort = ('created_at', True)
    
    # 編輯頁面設定
    form_excluded_columns = ['created_at', 'updated_at']
    
    # 自訂表單欄位
    form_overrides = {
        'comment_text': TextAreaField,
        'rating': SelectField
    }
    
    form_args = {
        'rating': {
            'choices': [(1, '1 星'), (2, '2 星'), (3, '3 星'), (4, '4 星'), (5, '5 星')],
            'validators': [DataRequired()]
        },
        'comment_text': {
            'validators': [Length(max=500)]
        }
    }
    
    # 自訂欄位標籤
    column_labels = {
        'review_id': 'ID',
        'user.display_name': '使用者',
        'movie.title': '電影',
        'rating': '評分',
        'comment_text': '評論內容',
        'created_at': '建立時間',
        'updated_at': '更新時間'
    }
    
    def is_accessible(self):
        return current_user.is_authenticated
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login', next=request.url))
    
    def after_model_change(self, form, model, is_created):
        """評論變更後重新計算電影評分"""
        if model.movie:
            model.movie.calculate_avg_rating()
        super().after_model_change(form, model, is_created)
    
    def after_model_delete(self, model):
        """評論刪除後重新計算電影評分"""
        if model.movie:
            model.movie.calculate_avg_rating()
        super().after_model_delete(model)


def register_admin_views(admin: Admin, db) -> None:
    """
    註冊管理後台視圖
    
    Args:
        admin: Flask-Admin 實例
        db: SQLAlchemy 實例
    """
    # 設定首頁視圖
    admin.index_view = AdminIndexView(name='儀表板', url='/admin')
    
    # 註冊模型視圖
    admin.add_view(UserModelView(User, db.session, name='使用者管理', category='使用者'))
    admin.add_view(MovieModelView(Movie, db.session, name='電影管理', category='內容'))
    admin.add_view(ReviewModelView(Review, db.session, name='評論管理', category='內容'))
    
    # 設定管理後台模板
    admin.template_mode = 'bootstrap4'
