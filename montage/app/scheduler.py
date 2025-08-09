"""
排程器 - 每日更新排行榜
"""
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from flask import Flask
from app import db
from app.models import Movie


def update_rankings() -> None:
    """
    更新電影排行榜
    根據 PRD.md 要求：依「評論數 ➜ 上映日」排序
    """
    try:
        logging.info('開始更新電影排行榜...')
        
        # 重新計算所有電影的平均評分
        movies = Movie.query.all()
        updated_count = 0
        
        for movie in movies:
            old_rating = movie.avg_rating
            movie.calculate_avg_rating()
            
            if old_rating != movie.avg_rating:
                updated_count += 1
        
        db.session.commit()
        
        logging.info(f'排行榜更新完成，共更新 {updated_count} 部電影的評分')
        
    except Exception as e:
        logging.error(f'更新排行榜時發生錯誤: {str(e)}')
        db.session.rollback()


def get_top_movies_by_reviews(limit: int = 50):
    """
    取得依評論數排序的熱門電影
    
    Args:
        limit: 限制數量
        
    Returns:
        電影列表，依評論數降序排列，相同評論數時依上映日降序
    """
    return db.session.query(Movie)\
        .join(Movie.reviews)\
        .group_by(Movie.movie_id)\
        .order_by(
            db.func.count(Movie.reviews).desc(),  # 評論數降序
            Movie.release_year.desc(),            # 上映年份降序
            Movie.created_at.desc()               # 建立時間降序
        )\
        .limit(limit)\
        .all()


def get_top_movies_by_rating(limit: int = 50, min_reviews: int = 5):
    """
    取得依評分排序的高分電影
    
    Args:
        limit: 限制數量
        min_reviews: 最少評論數要求
        
    Returns:
        電影列表，依平均評分降序排列
    """
    return db.session.query(Movie)\
        .join(Movie.reviews)\
        .group_by(Movie.movie_id)\
        .having(db.func.count(Movie.reviews) >= min_reviews)\
        .order_by(
            Movie.avg_rating.desc(),              # 平均評分降序
            db.func.count(Movie.reviews).desc(),  # 評論數降序
            Movie.release_year.desc()             # 上映年份降序
        )\
        .limit(limit)\
        .all()


def get_recent_movies(limit: int = 20):
    """
    取得最近上映的電影
    
    Args:
        limit: 限制數量
        
    Returns:
        電影列表，依上映年份降序排列
    """
    return Movie.query\
        .filter(Movie.release_year.isnot(None))\
        .order_by(
            Movie.release_year.desc(),
            Movie.created_at.desc()
        )\
        .limit(limit)\
        .all()


def get_hero_carousel_movies(limit: int = 5):
    """
    取得首頁輪播電影
    根據 PRD.md：5 張海報
    
    Args:
        limit: 限制數量（預設5張）
        
    Returns:
        電影列表，用於首頁輪播
    """
    # 選擇有海報且評論數較多的電影
    return db.session.query(Movie)\
        .filter(Movie.poster_url.isnot(None))\
        .filter(Movie.poster_url != '')\
        .join(Movie.reviews)\
        .group_by(Movie.movie_id)\
        .having(db.func.count(Movie.reviews) >= 3)\
        .order_by(
            db.func.count(Movie.reviews).desc(),
            Movie.avg_rating.desc(),
            Movie.release_year.desc()
        )\
        .limit(limit)\
        .all()


def cleanup_expired_tokens() -> None:
    """
    清理過期的確認令牌
    """
    try:
        from app.models import User
        from datetime import timedelta
        
        # 清理30分鐘前的令牌（假設重設連結30分鐘過期）
        expiry_time = datetime.utcnow() - timedelta(minutes=30)
        
        expired_users = User.query.filter(
            User.confirmation_token.isnot(None),
            User.created_at < expiry_time,
            User.email_confirmed == False
        ).all()
        
        for user in expired_users:
            user.confirmation_token = None
        
        if expired_users:
            db.session.commit()
            logging.info(f'已清理 {len(expired_users)} 個過期的確認令牌')
            
    except Exception as e:
        logging.error(f'清理過期令牌時發生錯誤: {str(e)}')
        db.session.rollback()


def start_scheduler(app: Flask) -> None:
    """
    啟動排程器
    
    Args:
        app: Flask 應用程式實例
    """
    scheduler = BackgroundScheduler()
    
    # 設定排程器的日誌記錄器
    logging.getLogger('apscheduler').setLevel(logging.WARNING)
    
    with app.app_context():
        # 每日 02:00 更新排行榜
        scheduler.add_job(
            func=lambda: app.app_context().push() or update_rankings(),
            trigger=CronTrigger(hour=2, minute=0),
            id='update_rankings',
            name='更新電影排行榜',
            replace_existing=True
        )
        
        # 每小時清理過期令牌
        scheduler.add_job(
            func=lambda: app.app_context().push() or cleanup_expired_tokens(),
            trigger=CronTrigger(minute=0),
            id='cleanup_tokens',
            name='清理過期令牌',
            replace_existing=True
        )
    
    try:
        scheduler.start()
        app.logger.info('排程器已啟動')
    except Exception as e:
        app.logger.error(f'排程器啟動失敗: {str(e)}')
    
    # 註冊應用程式關閉時的清理函數
    import atexit
    atexit.register(lambda: scheduler.shutdown())
