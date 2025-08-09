"""
認證表單
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length, ValidationError, NumberRange
)
from app.models import User


class LoginForm(FlaskForm):
    """登入表單"""
    
    email = StringField(
        '電子郵件',
        validators=[DataRequired(message='請輸入電子郵件'), Email(message='請輸入有效的電子郵件地址')],
        render_kw={'placeholder': '請輸入您的電子郵件', 'class': 'form-control'}
    )
    
    password = PasswordField(
        '密碼',
        validators=[DataRequired(message='請輸入密碼')],
        render_kw={'placeholder': '請輸入您的密碼', 'class': 'form-control'}
    )
    
    remember_me = BooleanField(
        '記住我',
        render_kw={'class': 'form-check-input'}
    )
    
    submit = SubmitField(
        '登入',
        render_kw={'class': 'btn btn-primary w-100'}
    )


class RegisterForm(FlaskForm):
    """註冊表單"""
    
    email = StringField(
        '電子郵件',
        validators=[
            DataRequired(message='請輸入電子郵件'),
            Email(message='請輸入有效的電子郵件地址'),
            Length(max=120, message='電子郵件地址不能超過120個字元')
        ],
        render_kw={'placeholder': '請輸入您的電子郵件', 'class': 'form-control'}
    )
    
    display_name = StringField(
        '顯示名稱',
        validators=[
            DataRequired(message='請輸入顯示名稱'),
            Length(min=2, max=80, message='顯示名稱必須在2-80個字元之間')
        ],
        render_kw={'placeholder': '請輸入您的顯示名稱', 'class': 'form-control'}
    )
    
    password = PasswordField(
        '密碼',
        validators=[
            DataRequired(message='請輸入密碼'),
            Length(min=8, message='密碼至少需要8個字元')
        ],
        render_kw={'placeholder': '請輸入密碼（至少8個字元）', 'class': 'form-control'}
    )
    
    password2 = PasswordField(
        '確認密碼',
        validators=[
            DataRequired(message='請確認密碼'),
            EqualTo('password', message='兩次輸入的密碼不一致')
        ],
        render_kw={'placeholder': '請再次輸入密碼', 'class': 'form-control'}
    )
    
    submit = SubmitField(
        '註冊',
        render_kw={'class': 'btn btn-primary w-100'}
    )
    
    def validate_email(self, email):
        """驗證電子郵件是否已存在"""
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError('此電子郵件已被註冊，請使用其他電子郵件地址。')


class ResetPasswordRequestForm(FlaskForm):
    """密碼重設要求表單"""
    
    email = StringField(
        '電子郵件',
        validators=[
            DataRequired(message='請輸入電子郵件'),
            Email(message='請輸入有效的電子郵件地址')
        ],
        render_kw={'placeholder': '請輸入您的電子郵件', 'class': 'form-control'}
    )
    
    submit = SubmitField(
        '發送重設連結',
        render_kw={'class': 'btn btn-primary w-100'}
    )


class ResetPasswordForm(FlaskForm):
    """密碼重設表單"""
    
    password = PasswordField(
        '新密碼',
        validators=[
            DataRequired(message='請輸入新密碼'),
            Length(min=8, message='密碼至少需要8個字元')
        ],
        render_kw={'placeholder': '請輸入新密碼（至少8個字元）', 'class': 'form-control'}
    )
    
    password2 = PasswordField(
        '確認新密碼',
        validators=[
            DataRequired(message='請確認新密碼'),
            EqualTo('password', message='兩次輸入的密碼不一致')
        ],
        render_kw={'placeholder': '請再次輸入新密碼', 'class': 'form-control'}
    )
    
    submit = SubmitField(
        '重設密碼',
        render_kw={'class': 'btn btn-primary w-100'}
    )


class ReviewForm(FlaskForm):
    """評論表單"""
    
    rating = StringField(
        '評分',
        validators=[DataRequired(message='請選擇評分')],
        render_kw={'type': 'hidden'}
    )
    
    comment_text = TextAreaField(
        '評論內容',
        validators=[
            Length(max=500, message='評論內容不能超過500個字元')
        ],
        render_kw={
            'placeholder': '分享您對這部電影的看法...（選填）',
            'class': 'form-control',
            'rows': 4
        }
    )
    
    submit = SubmitField(
        '提交評論',
        render_kw={'class': 'btn btn-primary'}
    )
    
    def validate_rating(self, rating):
        """驗證評分範圍"""
        try:
            rating_value = int(rating.data)
            if not 1 <= rating_value <= 5:
                raise ValidationError('評分必須在1-5星之間')
        except (ValueError, TypeError):
            raise ValidationError('請選擇有效的評分')


class SearchForm(FlaskForm):
    """搜尋表單"""
    
    q = StringField(
        '搜尋',
        validators=[Length(max=100, message='搜尋關鍵字不能超過100個字元')],
        render_kw={
            'placeholder': '搜尋電影標題、使用者或評論內容...',
            'class': 'form-control'
        }
    )
    
    submit = SubmitField(
        '搜尋',
        render_kw={'class': 'btn btn-outline-primary'}
    )
