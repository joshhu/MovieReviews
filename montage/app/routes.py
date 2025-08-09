"""
主要路由
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import or_, desc, func
from app import db
from app.models import Movie, Review, User
from app.auth.forms import ReviewForm, SearchForm
from app.scheduler import (
    get_top_movies_by_reviews, 
    get_top_movies_by_rating, 
    get_recent_movies,
    get_hero_carousel_movies
)

main = Blueprint('main', __name__)


@main.route('/')
def index():
    """首頁"""
    # 取得輪播電影
    hero_movies = get_hero_carousel_movies(5)
    
    # 取得熱門電影（依評論數）
    popular_movies = get_top_movies_by_reviews(8)
    
    # 取得高分電影
    top_rated_movies = get_top_movies_by_rating(8, min_reviews=3)
    
    # 取得最新電影
    recent_movies = get_recent_movies(8)
    
    # 最新評論
    latest_reviews = Review.query\
        .join(Movie)\
        .join(User)\
        .order_by(Review.created_at.desc())\
        .limit(6)\
        .all()
    
    return render_template(
        'index.html',
        hero_movies=hero_movies,
        popular_movies=popular_movies,
        top_rated_movies=top_rated_movies,
        recent_movies=recent_movies,
        latest_reviews=latest_reviews
    )


@main.route('/movies')
def movies():
    """電影列表頁面"""
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort', 'popular')  # popular, rating, recent, title
    genre = request.args.get('genre', '')
    year = request.args.get('year', '', type=str)
    rating_filter = request.args.get('rating', '', type=str)
    
    # 基礎查詢
    query = Movie.query
    
    # 類型篩選
    if genre:
        query = query.filter(Movie.genre_ids.contains(genre))
    
    # 年份篩選
    if year:
        try:
            year_int = int(year)
            query = query.filter(Movie.release_year == year_int)
        except ValueError:
            pass
    
    # 評分篩選（站內平均分）
    if rating_filter:
        try:
            rating_min = float(rating_filter)
            query = query.filter(Movie.avg_rating >= rating_min)
        except ValueError:
            pass
    
    # 排序
    # 為了支援依評論數排序，需要 left join Review 並 group_by
    if sort_by in ('popular', 'rating'):
        query = query.outerjoin(Review).group_by(Movie.movie_id)
    
    if sort_by == 'rating':
        # 先用站內 avg_rating（若為0或NULL）回退到 TMDb vote_average
        # 再以評論數、年份做次序
        sort_score = func.coalesce(func.nullif(Movie.avg_rating, 0.0), Movie.vote_average)
        query = query.order_by(
            desc(sort_score),
            desc(func.count(Review.review_id)),
            desc(Movie.release_year)
        )
    elif sort_by == 'recent':
        query = query.order_by(desc(Movie.release_year), desc(Movie.created_at))
    elif sort_by == 'title':
        query = query.order_by(Movie.title)
    else:  # popular（熱門度）：以評論數優先，回退 TMDb vote_average，再回退年份
        query = query.order_by(
            desc(func.count(Review.review_id)),
            desc(Movie.vote_average),
            desc(Movie.release_year),
            desc(Movie.created_at)
        )
    
    # 分頁
    per_page = current_app.config.get('MOVIES_PER_PAGE', 20)
    movies_pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    # 年份選單（近年優先）
    years = db.session.query(Movie.release_year)\
        .filter(Movie.release_year.isnot(None))\
        .distinct()\
        .order_by(desc(Movie.release_year))\
        .all()
    years = [year[0] for year in years]
    
    return render_template(
        'movies/list.html',
        movies=movies_pagination.items,
        pagination=movies_pagination,
        sort_by=sort_by,
        genre=genre,
        year=year,
        rating_filter=rating_filter,
        years=years
    )


@main.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    """電影詳情頁面"""
    movie = Movie.query.get_or_404(movie_id)
    
    # 取得電影評論（分頁）
    page = request.args.get('page', 1, type=int)
    reviews_pagination = Review.query\
        .filter_by(movie_id=movie_id)\
        .order_by(Review.created_at.desc())\
        .paginate(page=page, per_page=current_app.config.get('REVIEWS_PER_PAGE', 10), error_out=False)
    
    # 檢查當前使用者是否已評論
    user_review = None
    if current_user.is_authenticated:
        user_review = Review.query.filter_by(
            user_id=current_user.user_id,
            movie_id=movie_id
        ).first()
    
    # 評論表單
    review_form = ReviewForm()
    
    # 評分統計
    rating_stats = db.session.query(
        Review.rating,
        func.count(Review.rating).label('count')
    ).filter_by(movie_id=movie_id)\
     .group_by(Review.rating)\
     .all()
    
    rating_distribution = {i: 0 for i in range(1, 6)}
    total_reviews = 0
    for rating, count in rating_stats:
        rating_distribution[rating] = count
        total_reviews += count
    
    return render_template(
        'movies/detail.html',
        movie=movie,
        reviews=reviews_pagination.items,
        pagination=reviews_pagination,
        user_review=user_review,
        review_form=review_form,
        rating_distribution=rating_distribution,
        total_reviews=total_reviews
    )


@main.route('/movie/<int:movie_id>/review', methods=['POST'])
@login_required
def add_review(movie_id):
    """新增或更新評論"""
    movie = Movie.query.get_or_404(movie_id)
    form = ReviewForm()
    
    if form.validate_on_submit():
        # 檢查是否已有評論
        existing_review = Review.query.filter_by(
            user_id=current_user.user_id,
            movie_id=movie_id
        ).first()
        
        rating = int(form.rating.data)
        comment_text = form.comment_text.data.strip() if form.comment_text.data else None
        
        if existing_review:
            # 更新現有評論
            existing_review.rating = rating
            existing_review.comment_text = comment_text
            existing_review.updated_at = func.now()
        else:
            # 新增評論
            new_review = Review(
                user_id=current_user.user_id,
                movie_id=movie_id,
                rating=rating,
                comment_text=comment_text
            )
            db.session.add(new_review)
        
        db.session.commit()
        
        # 重新計算平均評分
        movie.calculate_avg_rating()
        
        flash('您的評論已提交！', 'success')
        return redirect(url_for('main.movie_detail', movie_id=movie_id))
    
    flash('提交失敗，請確認表單內容。', 'danger')
    return redirect(url_for('main.movie_detail', movie_id=movie_id))


@main.route('/review/<int:review_id>/delete', methods=['POST'])
@login_required
def delete_review(review_id: int):
    """刪除評論（與模板中的 url_for('main.delete_review') 對應）"""
    review = Review.query.get_or_404(review_id)
    
    # 權限檢查：僅作者可刪除
    if review.user_id != current_user.user_id:
        flash('您沒有權限刪除此評論。', 'danger')
        return redirect(url_for('main.movie_detail', movie_id=review.movie_id))
    
    movie_id = review.movie_id
    db.session.delete(review)
    db.session.commit()
    
    # 重新計算該電影平均評分
    movie = Movie.query.get(movie_id)
    if movie:
        movie.calculate_avg_rating()
    
    flash('評論已刪除。', 'success')
    return redirect(url_for('main.movie_detail', movie_id=movie_id))


@main.route('/search')
def search():
    """搜尋頁面"""
    form = SearchForm()
    movies = []
    users = []
    reviews = []
    
    query = request.args.get('q', '').strip()
    
    if query:
        # 電影搜尋
        movies = Movie.query.filter(
            or_(
                Movie.title.contains(query),
                Movie.overview.contains(query),
                Movie.tagline.contains(query)
            )
        ).order_by(desc(Movie.avg_rating)).limit(20).all()
        
        # 使用者搜尋
        users = User.query.filter(
            User.display_name.contains(query)
        ).filter(User.email_confirmed == True).limit(10).all()
        
        # 評論搜尋
        reviews = Review.query.join(Movie).join(User).filter(
            Review.comment_text.contains(query)
        ).order_by(desc(Review.created_at)).limit(15).all()
    
    return render_template(
        'search_results.html',
        form=form,
        query=query,
        movies=movies,
        users=users,
        reviews=reviews
    )


@main.route('/ranking')
def ranking():
    """排行榜頁面"""
    tab = request.args.get('tab', 'popular')  # popular, top_rated, recent
    
    if tab == 'top_rated':
        movies = get_top_movies_by_rating(50, min_reviews=5)
        title = '高分電影排行榜'
    elif tab == 'recent':
        movies = get_recent_movies(50)
        title = '最新電影'
    else:  # popular
        movies = get_top_movies_by_reviews(50)
        title = '熱門電影排行榜'
    
    return render_template(
        'ranking.html',
        movies=movies,
        tab=tab,
        title=title
    )


@main.route('/api/movie/<int:movie_id>/rating', methods=['GET'])
def get_movie_rating(movie_id):
    """API: 取得電影評分資訊"""
    movie = Movie.query.get_or_404(movie_id)
    
    # 評分統計
    rating_stats = db.session.query(
        Review.rating,
        func.count(Review.rating).label('count')
    ).filter_by(movie_id=movie_id)\
     .group_by(Review.rating)\
     .all()
    
    # 平均評分
    avg_rating = movie.avg_rating
    total_reviews = sum(count for _, count in rating_stats)
    
    return jsonify({
        'avg_rating': avg_rating,
        'total_reviews': total_reviews,
        'distribution': {str(rating): count for rating, count in rating_stats}
    })


@main.route('/user/<int:user_id>')
def user_profile(user_id):
    """使用者個人頁"""
    user = User.query.get_or_404(user_id)
    
    page = request.args.get('page', 1, type=int)
    reviews_pagination = Review.query\
        .filter_by(user_id=user_id)\
        .order_by(Review.created_at.desc())\
        .paginate(page=page, per_page=current_app.config.get('REVIEWS_PER_PAGE', 10), error_out=False)
    
    total_reviews = db.session.query(func.count(Review.review_id))\
        .filter_by(user_id=user_id).scalar()
    avg_rating_given = db.session.query(func.avg(Review.rating))\
        .filter_by(user_id=user_id).scalar()
    avg_rating_given = round(avg_rating_given, 2) if avg_rating_given else 0
    
    return render_template(
        'user_profile.html',
        user=user,
        reviews=reviews_pagination.items,
        pagination=reviews_pagination,
        total_reviews=total_reviews,
        avg_rating_given=avg_rating_given
    )
