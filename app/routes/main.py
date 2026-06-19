from datetime import date

from flask import Blueprint, render_template
from flask_login import current_user, login_required

from app.models import (
    HABIT_CATEGORIES,
    MOTIVATIONAL_QUOTES,
    TRANSFORMATION_PLAN,
    calculate_streak,
    get_daily_score,
    get_overall_progress,
    get_streak_badge,
)

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    if current_user.is_authenticated:
        return render_template("app.html")
    return render_template("landing.html")


@main_bp.route("/app")
@login_required
def dashboard():
    return render_template("app.html")


@main_bp.route("/api/dashboard-data")
@login_required
def dashboard_data():
    today = date.today()
    current_streak, longest_streak = calculate_streak(current_user.id)
    daily_score = get_daily_score(current_user.id)
    overall = get_overall_progress(current_user.id)
    badge = get_streak_badge(current_streak)
    quote_index = today.toordinal() % len(MOTIVATIONAL_QUOTES)

    return {
        "today": today.strftime("%A, %B %d, %Y"),
        "overall_progress": overall,
        "daily_score": daily_score,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "streak_badge": badge,
        "quote": MOTIVATIONAL_QUOTES[quote_index],
        "username": current_user.username,
    }
