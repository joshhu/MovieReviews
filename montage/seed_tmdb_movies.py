#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TMDb 電影資料庫種子腳本 - 符合PRD要求500部電影
運行此腳本將從TMDb API獲取500部真實電影並填充到資料庫
"""

import os
import requests
import time
from datetime import datetime
from app import create_app, db
from app.models import Movie

# TMDb API 設定
TMDB_API_KEY = os.getenv('TMDB_API_KEY', 'your-tmdb-api-key-here')
TMDB_BASE_URL = 'https://api.themoviedb.org/3'
TMDB_IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500'

def get_movies_from_tmdb(category='popular', total_needed=500):
    """
    從TMDb獲取電影列表
    
    Args:
        category: 電影類別 ('popular', 'top_rated', 'now_playing', 'upcoming')
        total_needed: 需要的總電影數量
        
    Returns:
        電影列表
    """
    movies = []
    page = 1
    max_pages = 25  # TMDb API 限制最多500頁，每頁20部電影
    
    print(f"🎬 從TMDb獲取 {category} 電影...")
    
    while len(movies) < total_needed and page <= max_pages:
        try:
            url = f"{TMDB_BASE_URL}/movie/{category}"
            params = {
                'api_key': TMDB_API_KEY,
                'language': 'zh-TW',
                'page': page
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'results' in data and data['results']:
                movies.extend(data['results'])
                print(f"✅ 已獲取第 {page} 頁，共 {len(data['results'])} 部電影 (累計: {len(movies)})")
                page += 1
                time.sleep(0.25)  # 避免API限制
            else:
                print(f"⚠️ 第 {page} 頁無資料，停止獲取")
                break
                
        except requests.RequestException as e:
            print(f"❌ 第 {page} 頁獲取失敗: {e}")
            page += 1
            continue
        except KeyboardInterrupt:
            print("\n⚠️ 用戶中斷操作")
            break
    
    return movies[:total_needed]

def get_movie_details(movie_id):
    """
    獲取電影詳細資訊
    
    Args:
        movie_id: TMDb電影ID
        
    Returns:
        電影詳細資訊
    """
    try:
        url = f"{TMDB_BASE_URL}/movie/{movie_id}"
        params = {
            'api_key': TMDB_API_KEY,
            'language': 'zh-TW'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
        
    except requests.RequestException:
        return None

def seed_database():
    """填充資料庫"""
    print("🚀 開始TMDb電影資料庫種子腳本")
    print("=" * 50)
    
    # 檢查API Key
    if TMDB_API_KEY == 'your-tmdb-api-key-here':
        print("❌ 請設定有效的TMDB_API_KEY環境變數")
        print("📋 獲取方式: https://www.themoviedb.org/settings/api")
        return False
    
    app = create_app()
    
    with app.app_context():
        # 檢查目前電影數量
        current_count = Movie.query.count()
        print(f"📊 目前資料庫電影數量: {current_count}")
        
        if current_count >= 500:
            print("✅ 資料庫已有足夠電影，無需新增")
            return True
        
        needed = 500 - current_count
        print(f"🎯 需要新增 {needed} 部電影以達到PRD要求的500部")
        
        # 確認操作
        confirm = input("\n確定要從TMDb獲取電影資料嗎？(y/N): ")
        if confirm.lower() != 'y':
            print("❌ 操作已取消")
            return False
        
        print("\n📡 開始從TMDb獲取電影資料...")
        
        # 獲取不同類別的電影以確保多樣性
        all_movies = []
        categories = [
            ('popular', min(200, needed)),          # 熱門電影
            ('top_rated', min(200, needed//2)),     # 高評分電影  
            ('now_playing', min(100, needed//4)),   # 現正上映
        ]
        
        for category, count in categories:
            if len(all_movies) >= needed:
                break
            movies = get_movies_from_tmdb(category, count)
            all_movies.extend(movies)
        
        # 去重（基於tmdb_id）
        seen_ids = set()
        unique_movies = []
        for movie in all_movies:
            if movie['id'] not in seen_ids:
                seen_ids.add(movie['id'])
                unique_movies.append(movie)
        
        print(f"\n🎬 準備新增 {len(unique_movies)} 部去重後的電影...")
        
        added_count = 0
        failed_count = 0
        
        for i, movie_data in enumerate(unique_movies[:needed]):
            try:
                # 檢查是否已存在
                existing = Movie.query.filter_by(tmdb_id=movie_data['id']).first()
                if existing:
                    continue
                
                # 獲取詳細資訊
                details = get_movie_details(movie_data['id'])
                if details:
                    movie_data.update(details)
                
                # 處理海報URL
                poster_path = movie_data.get('poster_path')
                poster_url = f"{TMDB_IMAGE_BASE_URL}{poster_path}" if poster_path else ""
                
                # 處理發行年份
                release_date = movie_data.get('release_date', '')
                release_year = int(release_date[:4]) if release_date and len(release_date) >= 4 else None
                
                # 處理類型ID
                genres = movie_data.get('genres', [])
                genre_ids = ','.join([str(g['id']) for g in genres]) if genres else ''
                
                # 創建電影記錄
                movie = Movie(
                    title=movie_data.get('title', '未知電影'),
                    release_year=release_year,
                    poster_url=poster_url,
                    genre_ids=genre_ids,
                    runtime=movie_data.get('runtime'),
                    tagline=movie_data.get('tagline', ''),
                    overview=movie_data.get('overview', ''),
                    vote_average=float(movie_data.get('vote_average', 0.0)),
                    tmdb_id=movie_data['id'],
                    avg_rating=0.0,
                    created_at=datetime.utcnow()
                )
                
                db.session.add(movie)
                added_count += 1
                
                # 每50部提交一次
                if added_count % 50 == 0:
                    db.session.commit()
                    print(f"💾 已新增 {added_count} 部電影...")
                
                # 避免API限制
                if i % 10 == 0:
                    time.sleep(0.5)
                    
            except Exception as e:
                failed_count += 1
                print(f"❌ 處理電影失敗: {e}")
                continue
        
        # 最終提交
        db.session.commit()
        
        # 統計結果
        final_count = Movie.query.count()
        movies_with_posters = Movie.query.filter(
            Movie.poster_url != '', 
            Movie.poster_url.isnot(None)
        ).count()
        
        print(f"\n🎉 種子腳本執行完成！")
        print(f"📊 最終統計:")
        print(f"   • 總電影數: {final_count}")
        print(f"   • 新增電影數: {added_count}")
        print(f"   • 有海報的電影: {movies_with_posters}")
        print(f"   • 海報覆蓋率: {(movies_with_posters/final_count*100):.1f}%")
        print(f"   • 失敗數: {failed_count}")
        
        if final_count >= 500:
            print("✅ 已達到PRD要求的500部電影！")
        else:
            print(f"⚠️ 距離500部電影目標還差 {500 - final_count} 部")
        
        return True

if __name__ == '__main__':
    try:
        success = seed_database()
        if success:
            print("\n🍿 現在可以啟動應用程式查看結果！")
            print("   python run.py")
        else:
            print("\n❌ 種子腳本執行失敗")
    except KeyboardInterrupt:
        print("\n⚠️ 程式被用戶中斷")
    except Exception as e:
        print(f"\n💥 發生錯誤: {e}")

