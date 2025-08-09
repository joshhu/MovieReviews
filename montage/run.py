"""
蒙太奇之愛 - 應用程式啟動檔案
"""
import os
from app import create_app

# 建立 Flask 應用程式實例
app = create_app()

if __name__ == '__main__':
    # 建立日誌目錄
    log_dir = os.path.dirname(app.config.get('LOG_FILE', 'logs/app.log'))
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 啟動開發伺服器
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=app.config.get('DEBUG', False)
    )
