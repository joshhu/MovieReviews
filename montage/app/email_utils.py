"""
郵件發送工具 (Gmail SMTP)
"""
from flask import current_app, url_for
from flask_mail import Message
from app import mail
from typing import Optional


def send_confirmation_email(user) -> None:
    """
    發送電子郵件確認信件
    
    Args:
        user: 使用者物件
    """
    token = user.confirmation_token
    confirm_url = url_for('auth.confirm_email', token=token, _external=True)
    
    subject = '蒙太奇之愛 - 確認您的電子郵件'
    
    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background-color: #f8f9fa; padding: 20px; text-align: center;">
            <h1 style="color: #343a40; margin: 0;">蒙太奇之愛</h1>
            <p style="color: #6c757d; margin: 10px 0;">電影評論社區</p>
        </div>
        
        <div style="padding: 30px 20px;">
            <h2 style="color: #343a40;">歡迎加入蒙太奇之愛！</h2>
            
            <p>親愛的 <strong>{user.display_name}</strong>，</p>
            
            <p>感謝您註冊蒙太奇之愛！為了確保您的帳戶安全，請點選下方連結確認您的電子郵件地址：</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{confirm_url}" 
                   style="background-color: #007bff; color: white; padding: 12px 30px; 
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                    確認電子郵件
                </a>
            </div>
            
            <p>如果上方按鈕無法點選，請複製下方連結到瀏覽器網址列：</p>
            <p style="word-break: break-all; color: #6c757d; font-size: 14px;">{confirm_url}</p>
            
            <hr style="margin: 30px 0; border: none; height: 1px; background-color: #dee2e6;">
            
            <p style="color: #6c757d; font-size: 14px;">
                此信件由系統自動發送，請勿回覆。<br>
                如有任何問題，請聯繫我們的客服團隊。
            </p>
        </div>
    </div>
    """
    
    text_body = f"""
蒙太奇之愛 - 確認您的電子郵件

親愛的 {user.display_name}，

感謝您註冊蒙太奇之愛！為了確保您的帳戶安全，請點選下方連結確認您的電子郵件地址：

{confirm_url}

此信件由系統自動發送，請勿回覆。
如有任何問題，請聯繫我們的客服團隊。

蒙太奇之愛團隊
    """
    
    send_email(
        subject=subject,
        recipient=user.email,
        text_body=text_body,
        html_body=html_body
    )


def send_password_reset_email(user, token: str) -> None:
    """
    發送密碼重設信件
    
    Args:
        user: 使用者物件
        token: 重設令牌
    """
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    
    subject = '蒙太奇之愛 - 密碼重設'
    
    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background-color: #f8f9fa; padding: 20px; text-align: center;">
            <h1 style="color: #343a40; margin: 0;">蒙太奇之愛</h1>
            <p style="color: #6c757d; margin: 10px 0;">電影評論社區</p>
        </div>
        
        <div style="padding: 30px 20px;">
            <h2 style="color: #343a40;">密碼重設要求</h2>
            
            <p>親愛的 <strong>{user.display_name}</strong>，</p>
            
            <p>我們收到了您的密碼重設要求。如果這不是您本人的操作，請忽略此信件。</p>
            
            <p>要重設您的密碼，請點選下方連結：</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}" 
                   style="background-color: #dc3545; color: white; padding: 12px 30px; 
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                    重設密碼
                </a>
            </div>
            
            <p style="color: #856404; background-color: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107;">
                <strong>安全提醒：</strong>此連結將在30分鐘後過期，為了您的帳戶安全，請盡快完成密碼重設。
            </p>
            
            <p>如果上方按鈕無法點選，請複製下方連結到瀏覽器網址列：</p>
            <p style="word-break: break-all; color: #6c757d; font-size: 14px;">{reset_url}</p>
            
            <hr style="margin: 30px 0; border: none; height: 1px; background-color: #dee2e6;">
            
            <p style="color: #6c757d; font-size: 14px;">
                此信件由系統自動發送，請勿回覆。<br>
                如有任何問題，請聯繫我們的客服團隊。
            </p>
        </div>
    </div>
    """
    
    text_body = f"""
蒙太奇之愛 - 密碼重設

親愛的 {user.display_name}，

我們收到了您的密碼重設要求。如果這不是您本人的操作，請忽略此信件。

要重設您的密碼，請點選下方連結：
{reset_url}

安全提醒：此連結將在30分鐘後過期，為了您的帳戶安全，請盡快完成密碼重設。

此信件由系統自動發送，請勿回覆。
如有任何問題，請聯繫我們的客服團隊。

蒙太奇之愛團隊
    """
    
    send_email(
        subject=subject,
        recipient=user.email,
        text_body=text_body,
        html_body=html_body
    )


def send_email(subject: str, recipient: str, text_body: str, html_body: Optional[str] = None) -> None:
    """
    發送電子郵件
    
    Args:
        subject: 信件主旨
        recipient: 收件人
        text_body: 純文字內容
        html_body: HTML 內容（選填）
    """
    msg = Message(
        subject=subject,
        recipients=[recipient],
        body=text_body,
        html=html_body
    )
    
    try:
        mail.send(msg)
        current_app.logger.info(f'郵件已發送至 {recipient}: {subject}')
    except Exception as e:
        current_app.logger.error(f'郵件發送失敗 {recipient}: {str(e)}')
        raise e
