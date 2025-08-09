"""
認證 Blueprint
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.auth.forms import LoginForm, RegisterForm, ResetPasswordRequestForm
from app.email_utils import send_confirmation_email, send_password_reset_email
import secrets
from datetime import datetime, timedelta

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """登入頁面"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        
        if user and user.check_password(form.password.data):
            if not user.email_confirmed:
                flash('請先確認您的電子郵件信箱。', 'warning')
                return redirect(url_for('auth.login'))
            
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.index'))
        else:
            flash('電子郵件或密碼錯誤。', 'danger')
    
    return render_template('auth/login.html', title='登入', form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """註冊頁面"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        # 檢查電子郵件是否已存在
        if User.query.filter_by(email=form.email.data.lower()).first():
            flash('此電子郵件已被註冊。', 'danger')
            return redirect(url_for('auth.register'))
        
        # 建立新使用者
        user = User(
            email=form.email.data.lower(),
            password=form.password.data,
            display_name=form.display_name.data
        )
        
        # 產生確認令牌
        user.confirmation_token = secrets.token_urlsafe(32)
        
        db.session.add(user)
        db.session.commit()
        
        # 發送確認信件
        try:
            send_confirmation_email(user)
            flash('註冊成功！請檢查您的電子郵件信箱並點選確認連結。', 'success')
        except Exception as e:
            current_app.logger.error(f'無法發送確認信件: {str(e)}')
            flash('註冊成功，但無法發送確認信件。請聯繫管理員。', 'warning')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='註冊', form=form)


@bp.route('/logout')
@login_required
def logout():
    """登出"""
    logout_user()
    flash('您已成功登出。', 'info')
    return redirect(url_for('main.index'))


@bp.route('/confirm/<token>')
def confirm_email(token):
    """確認電子郵件"""
    user = User.query.filter_by(confirmation_token=token).first()
    
    if not user:
        flash('無效的確認連結。', 'danger')
        return redirect(url_for('auth.login'))
    
    if user.email_confirmed:
        flash('您的電子郵件已經確認過了。', 'info')
        return redirect(url_for('auth.login'))
    
    user.email_confirmed = True
    user.confirmation_token = None
    db.session.commit()
    
    flash('電子郵件確認成功！您現在可以登入了。', 'success')
    return redirect(url_for('auth.login'))


@bp.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    """密碼重設要求"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        
        if user and user.email_confirmed:
            # 產生重設令牌
            reset_token = secrets.token_urlsafe(32)
            user.confirmation_token = reset_token  # 重用此欄位
            db.session.commit()
            
            try:
                send_password_reset_email(user, reset_token)
                flash('密碼重設信件已發送到您的電子郵件信箱。', 'info')
            except Exception as e:
                current_app.logger.error(f'無法發送密碼重設信件: {str(e)}')
                flash('無法發送密碼重設信件。請稍後再試。', 'danger')
        else:
            # 即使找不到使用者也顯示相同訊息，避免電子郵件枚舉攻擊
            flash('如果該電子郵件存在於我們的系統中，您將收到密碼重設信件。', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_request.html', title='重設密碼', form=form)


@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """密碼重設"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    user = User.query.filter_by(confirmation_token=token).first()
    
    if not user:
        flash('無效或過期的重設連結。', 'danger')
        return redirect(url_for('auth.login'))
    
    from app.auth.forms import ResetPasswordForm
    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.confirmation_token = None
        db.session.commit()
        
        flash('密碼重設成功！請使用新密碼登入。', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', title='重設密碼', form=form)
