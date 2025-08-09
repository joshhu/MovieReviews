#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
電影海報檢查和修復工具
檢查所有電影的海報是否可以正常訪問，並提供修復選項
"""

import requests
import time
from app import create_app, db
from app.models import Movie

def check_poster_url(url, timeout=10):
    """
    檢查海報URL是否可以訪問
    
    Args:
        url: 海報URL
        timeout: 超時時間
        
    Returns:
        (status_code, is_valid)
    """
    try:
        response = requests.head(url, timeout=timeout)
        return response.status_code, response.status_code == 200
    except:
        return 0, False

def fix_broken_posters():
    """檢查並修復損壞的海報"""
    
    app = create_app()
    with app.app_context():
        print("🔍 開始檢查所有電影海報...")
        
        all_movies = Movie.query.all()
        total_count = len(all_movies)
        broken_count = 0
        fixed_count = 0
        
        print(f"📊 總共 {total_count} 部電影需要檢查")
        
        # 備用海報URL (高品質通用海報)
        fallback_posters = [
            "https://image.tmdb.org/t/p/w500/wwemzKWzjKYJFfCeiB57q3r4Bcm.png",  # 通用電影海報 1
            "https://via.placeholder.com/500x750/1a1a1a/ffffff?text=🎬+電影海報",      # 簡潔海報
            "https://via.placeholder.com/500x750/2d3748/ffffff?text=📽️+Movie+Poster", # 英文海報
        ]
        
        for i, movie in enumerate(all_movies, 1):
            print(f"\r處理進度: {i}/{total_count} ({i/total_count*100:.1f}%)", end="", flush=True)
            
            if not movie.poster_url:
                print(f"\n⚠️ {movie.title}: 沒有海報URL")
                # 為沒有海報的電影設定備用海報
                movie.poster_url = fallback_posters[0]
                fixed_count += 1
                continue
            
            status_code, is_valid = check_poster_url(movie.poster_url)
            
            if not is_valid:
                print(f"\n❌ {movie.title}: 海報無法訪問 (狀態碼: {status_code})")
                print(f"   損壞URL: {movie.poster_url}")
                
                # 嘗試使用備用海報
                movie.poster_url = fallback_posters[broken_count % len(fallback_posters)]
                print(f"   修復URL: {movie.poster_url}")
                
                broken_count += 1
                fixed_count += 1
            
            # 避免請求過於頻繁
            if i % 10 == 0:
                time.sleep(0.5)
        
        # 提交更改
        if fixed_count > 0:
            db.session.commit()
            print(f"\n\n💾 已提交 {fixed_count} 項修復")
        
        print(f"\n\n📊 檢查結果:")
        print(f"   • 總電影數: {total_count}")
        print(f"   • 損壞海報: {broken_count}")
        print(f"   • 已修復: {fixed_count}")
        print(f"   • 正常海報: {total_count - broken_count}")
        
        if broken_count == 0:
            print("🎉 所有電影海報都正常！")
        else:
            print(f"✅ 已修復 {fixed_count} 個海報問題")

def check_specific_movie(movie_title):
    """檢查特定電影的海報"""
    
    app = create_app()
    with app.app_context():
        movie = Movie.query.filter(Movie.title.like(f'%{movie_title}%')).first()
        
        if not movie:
            print(f"❌ 找不到電影: {movie_title}")
            return
        
        print(f"🎬 檢查電影: {movie.title}")
        print(f"📅 發行年份: {movie.release_year}")
        print(f"🖼️ 海報URL: {movie.poster_url}")
        
        if movie.poster_url:
            status_code, is_valid = check_poster_url(movie.poster_url)
            status = "✅ 正常" if is_valid else f"❌ 無法訪問 (狀態碼: {status_code})"
            print(f"🔍 海報狀態: {status}")
        else:
            print("⚠️ 沒有海報URL")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        # 檢查特定電影
        movie_title = sys.argv[1]
        check_specific_movie(movie_title)
    else:
        # 檢查所有電影
        print("🛠️ 電影海報檢查和修復工具")
        print("=" * 40)
        
        choice = input("選擇操作:\n1. 檢查並修復所有電影海報\n2. 只檢查不修復\n請輸入 (1/2): ")
        
        if choice == '1':
            fix_broken_posters()
        elif choice == '2':
            # 只檢查，不修復
            app = create_app()
            with app.app_context():
                movies = Movie.query.limit(10).all()
                for movie in movies:
                    if movie.poster_url:
                        status_code, is_valid = check_poster_url(movie.poster_url)
                        status = "✅" if is_valid else "❌"
                        print(f"{status} {movie.title}: {status_code}")
        else:
            print("❌ 無效選擇")
            
        print("\n🍿 完成！現在可以查看電影海報了")

