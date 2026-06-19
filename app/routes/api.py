from datetime import date, timedelta

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from app import db
from app.models import (
    CAREER_SKILLS,
    FEAR_CHALLENGES,
    HABIT_CATEGORIES,
    MOOD_OPTIONS,
    TRANSFORMATION_PLAN,
    CareerProgress,
    FearChallenge,
    HabitEntry,
    MonthlyGoal,
    MonthlyPlan,
    MoodEntry,
    PlanProgress,
    WeeklyReview,
    calculate_streak,
    get_daily_score,
    get_overall_progress,
    get_streak_badge,
    get_week_start,
)

api_bp = Blueprint("api", __name__)


@api_bp.route("/habits", methods=["GET"])
@login_required
def get_habits():
    target_date = request.args.get("date", date.today().isoformat())
    try:
        entry_date = date.fromisoformat(target_date)
    except ValueError:
        entry_date = date.today()

    entries = {
        e.habit_name: e.completed
        for e in HabitEntry.query.filter_by(user_id=current_user.id, entry_date=entry_date).all()
    }

    habits = [{"name": h, "completed": entries.get(h, False)} for h in HABIT_CATEGORIES]
    score = get_daily_score(current_user.id, entry_date)

    return jsonify({"habits": habits, "date": entry_date.isoformat(), "score": score})


@api_bp.route("/habits", methods=["POST"])
@login_required
def save_habits():
    data = request.get_json()
    target_date = data.get("date", date.today().isoformat())
    habits = data.get("habits", [])

    try:
        entry_date = date.fromisoformat(target_date)
    except ValueError:
        return jsonify({"error": "Invalid date"}), 400

    for habit in habits:
        name = habit.get("name")
        completed = habit.get("completed", False)
        if name not in HABIT_CATEGORIES:
            continue

        entry = HabitEntry.query.filter_by(
            user_id=current_user.id, entry_date=entry_date, habit_name=name
        ).first()

        if entry:
            entry.completed = completed
        else:
            db.session.add(
                HabitEntry(user_id=current_user.id, entry_date=entry_date, habit_name=name, completed=completed)
            )

    db.session.commit()
    score = get_daily_score(current_user.id, entry_date)
    current_streak, longest_streak = calculate_streak(current_user.id)

    return jsonify({
        "success": True,
        "score": score,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "badge": get_streak_badge(current_streak),
    })


@api_bp.route("/streaks", methods=["GET"])
@login_required
def get_streaks():
    current_streak, longest_streak = calculate_streak(current_user.id)
    badge = get_streak_badge(current_streak)

    history = []
    for i in range(30):
        d = date.today() - timedelta(days=i)
        entries = HabitEntry.query.filter_by(user_id=current_user.id, entry_date=d).all()
        completed = sum(1 for e in entries if e.completed)
        history.append({
            "date": d.isoformat(),
            "completed": completed,
            "total": len(HABIT_CATEGORIES),
            "percentage": round((completed / len(HABIT_CATEGORIES)) * 100) if HABIT_CATEGORIES else 0,
        })

    return jsonify({
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "badge": badge,
        "history": history,
    })


@api_bp.route("/career-progress", methods=["GET"])
@login_required
def get_career_progress():
    progress = CareerProgress.query.filter_by(user_id=current_user.id).all()
    return jsonify({
        "skills": [{"name": p.skill_name, "percentage": p.percentage} for p in progress],
        "overall": get_overall_progress(current_user.id),
    })


@api_bp.route("/career-progress", methods=["POST"])
@login_required
def update_career_progress():
    data = request.get_json()
    skills = data.get("skills", [])

    for skill in skills:
        name = skill.get("name")
        percentage = min(100, max(0, int(skill.get("percentage", 0))))

        entry = CareerProgress.query.filter_by(user_id=current_user.id, skill_name=name).first()
        if entry:
            entry.percentage = percentage

    db.session.commit()
    return jsonify({"success": True, "overall": get_overall_progress(current_user.id)})


@api_bp.route("/fear-challenges", methods=["GET"])
@login_required
def get_fear_challenges():
    challenges = FearChallenge.query.filter_by(user_id=current_user.id).order_by(
        FearChallenge.completed_date.desc()
    ).all()

    return jsonify({
        "types": FEAR_CHALLENGES,
        "history": [
            {
                "id": c.id,
                "type": c.challenge_type,
                "date": c.completed_date.isoformat(),
                "notes": c.notes,
            }
            for c in challenges
        ],
    })


@api_bp.route("/fear-challenges", methods=["POST"])
@login_required
def add_fear_challenge():
    data = request.get_json()
    challenge_type = data.get("type")
    notes = data.get("notes", "")

    if challenge_type not in FEAR_CHALLENGES:
        return jsonify({"error": "Invalid challenge type"}), 400

    challenge = FearChallenge(
        user_id=current_user.id,
        challenge_type=challenge_type,
        completed_date=date.today(),
        notes=notes,
    )
    db.session.add(challenge)
    db.session.commit()

    return jsonify({"success": True, "id": challenge.id})


@api_bp.route("/fear-challenges/<int:challenge_id>", methods=["DELETE"])
@login_required
def delete_fear_challenge(challenge_id):
    challenge = FearChallenge.query.filter_by(id=challenge_id, user_id=current_user.id).first()
    if not challenge:
        return jsonify({"error": "Not found"}), 404

    db.session.delete(challenge)
    db.session.commit()
    return jsonify({"success": True})


@api_bp.route("/weekly-review", methods=["GET"])
@login_required
def get_weekly_review():
    week_start = get_week_start()
    review = WeeklyReview.query.filter_by(user_id=current_user.id, week_start=week_start).first()

    if review:
        return jsonify({
            "week_start": review.week_start.isoformat(),
            "wins": review.wins,
            "mistakes": review.mistakes,
            "lessons": review.lessons,
            "goals": review.goals,
        })

    return jsonify({
        "week_start": week_start.isoformat(),
        "wins": "",
        "mistakes": "",
        "lessons": "",
        "goals": "",
    })


@api_bp.route("/weekly-review", methods=["POST"])
@login_required
def save_weekly_review():
    data = request.get_json()
    week_start = get_week_start()

    review = WeeklyReview.query.filter_by(user_id=current_user.id, week_start=week_start).first()
    if not review:
        review = WeeklyReview(user_id=current_user.id, week_start=week_start)
        db.session.add(review)

    review.wins = data.get("wins", "")
    review.mistakes = data.get("mistakes", "")
    review.lessons = data.get("lessons", "")
    review.goals = data.get("goals", "")

    db.session.commit()
    return jsonify({"success": True})


@api_bp.route("/monthly-goals", methods=["GET"])
@login_required
def get_monthly_goals():
    plans = MonthlyPlan.query.filter_by(user_id=current_user.id).order_by(MonthlyPlan.created_at.asc()).all()
    result = []
    for plan in plans:
        goals = plan.goals.order_by(MonthlyGoal.created_at.asc()).all()
        completed = len(goals) > 0 and all(g.completed for g in goals)
        progress = round(sum(g.current_percentage for g in goals) / len(goals)) if goals else 0
        result.append({
            "id": plan.id,
            "name": plan.month_name,
            "completed": completed,
            "progress": progress,
            "goals": [
                {
                    "id": g.id,
                    "name": g.goal_name,
                    "current": g.current_percentage,
                    "completed": g.completed,
                }
                for g in goals
            ]
        })
    return jsonify({"plans": result})


@api_bp.route("/monthly-goals", methods=["POST"])
@login_required
def update_monthly_goals():
    data = request.get_json()
    goals = data.get("goals", [])

    for goal_data in goals:
        goal_id = goal_data.get("id")
        goal = MonthlyGoal.query.filter_by(id=goal_id, user_id=current_user.id).first()
        if goal:
            goal.current_percentage = min(100, max(0, int(goal_data.get("current", 0))))
            goal.completed = goal.current_percentage >= 100

    db.session.commit()
    return jsonify({"success": True})


@api_bp.route("/monthly-goals/create-plan", methods=["POST"])
@login_required
def create_monthly_plan():
    data = request.get_json()
    month_name = data.get("month_name", "").strip()
    if not month_name:
        return jsonify({"error": "Month name is required"}), 400

    existing = MonthlyPlan.query.filter_by(user_id=current_user.id, month_name=month_name).first()
    if existing:
        return jsonify({"error": f"Month '{month_name}' already exists"}), 400

    plan = MonthlyPlan(user_id=current_user.id, month_name=month_name)
    db.session.add(plan)
    db.session.commit()
    return jsonify({"success": True, "id": plan.id, "name": plan.month_name})


@api_bp.route("/monthly-goals/add-goal", methods=["POST"])
@login_required
def add_monthly_goal():
    data = request.get_json()
    plan_id = data.get("plan_id")
    goal_name = data.get("goal_name", "").strip()
    if not goal_name:
        return jsonify({"error": "Goal name is required"}), 400

    plan = MonthlyPlan.query.filter_by(id=plan_id, user_id=current_user.id).first()
    if not plan:
        return jsonify({"error": "Monthly plan not found"}), 404

    if plan.goals.count() >= 6:
        return jsonify({"error": "Maximum of 6 goals allowed per month"}), 400

    existing = MonthlyGoal.query.filter_by(plan_id=plan.id, goal_name=goal_name).first()
    if existing:
        return jsonify({"error": f"Goal '{goal_name}' already exists in this month"}), 400

    goal = MonthlyGoal(user_id=current_user.id, plan_id=plan.id, goal_name=goal_name)
    db.session.add(goal)
    db.session.commit()
    return jsonify({"success": True, "id": goal.id, "name": goal.goal_name})


@api_bp.route("/monthly-goals/edit-goal", methods=["POST"])
@login_required
def edit_monthly_goal():
    data = request.get_json()
    goal_id = data.get("goal_id")
    new_name = data.get("goal_name", "").strip()
    if not new_name:
        return jsonify({"error": "Goal name is required"}), 400

    goal = MonthlyGoal.query.filter_by(id=goal_id, user_id=current_user.id).first()
    if not goal:
        return jsonify({"error": "Goal not found"}), 404

    existing = MonthlyGoal.query.filter_by(plan_id=goal.plan_id, goal_name=new_name).first()
    if existing and existing.id != goal.id:
        return jsonify({"error": f"Goal '{new_name}' already exists in this month"}), 400

    goal.goal_name = new_name
    db.session.commit()
    return jsonify({"success": True})


@api_bp.route("/monthly-goals/delete-goal/<int:goal_id>", methods=["DELETE"])
@login_required
def delete_monthly_goal(goal_id):
    goal = MonthlyGoal.query.filter_by(id=goal_id, user_id=current_user.id).first()
    if not goal:
        return jsonify({"error": "Goal not found"}), 404

    db.session.delete(goal)
    db.session.commit()
    return jsonify({"success": True})


@api_bp.route("/monthly-goals/delete-plan/<int:plan_id>", methods=["DELETE"])
@login_required
def delete_monthly_plan(plan_id):
    plan = MonthlyPlan.query.filter_by(id=plan_id, user_id=current_user.id).first()
    if not plan:
        return jsonify({"error": "Monthly plan not found"}), 404

    db.session.delete(plan)
    db.session.commit()
    return jsonify({"success": True})


@api_bp.route("/mood", methods=["GET"])
@login_required
def get_mood():
    today = date.today()
    entry = MoodEntry.query.filter_by(user_id=current_user.id, entry_date=today).first()

    history = []
    for i in range(30):
        d = today - timedelta(days=i)
        e = MoodEntry.query.filter_by(user_id=current_user.id, entry_date=d).first()
        history.append({"date": d.isoformat(), "mood": e.mood if e else None})

    mood_counts = {m: 0 for m in MOOD_OPTIONS}
    for e in MoodEntry.query.filter_by(user_id=current_user.id).all():
        if e.mood in mood_counts:
            mood_counts[e.mood] += 1

    return jsonify({
        "options": MOOD_OPTIONS,
        "today": entry.mood if entry else None,
        "history": history,
        "counts": mood_counts,
    })


@api_bp.route("/mood", methods=["POST"])
@login_required
def save_mood():
    data = request.get_json()
    mood = data.get("mood")

    if mood not in MOOD_OPTIONS:
        return jsonify({"error": "Invalid mood"}), 400

    today = date.today()
    entry = MoodEntry.query.filter_by(user_id=current_user.id, entry_date=today).first()

    if entry:
        entry.mood = mood
    else:
        db.session.add(MoodEntry(user_id=current_user.id, entry_date=today, mood=mood))

    db.session.commit()
    return jsonify({"success": True})


@api_bp.route("/analytics", methods=["GET"])
@login_required
def get_analytics():
    today = date.today()

    habit_rate = []
    for i in range(7):
        d = today - timedelta(days=6 - i)
        entries = HabitEntry.query.filter_by(user_id=current_user.id, entry_date=d).all()
        completed = sum(1 for e in entries if e.completed)
        habit_rate.append({
            "date": d.strftime("%a"),
            "rate": round((completed / len(HABIT_CATEGORIES)) * 100) if HABIT_CATEGORIES else 0,
        })

    weekly_consistency = []
    for w in range(4):
        week_end = today - timedelta(days=w * 7)
        week_start = week_end - timedelta(days=6)
        total_completed = 0
        total_possible = 0
        for d_offset in range(7):
            d = week_start + timedelta(days=d_offset)
            entries = HabitEntry.query.filter_by(user_id=current_user.id, entry_date=d).all()
            total_completed += sum(1 for e in entries if e.completed)
            total_possible += len(HABIT_CATEGORIES)
        weekly_consistency.append({
            "week": f"Week {4 - w}",
            "rate": round((total_completed / total_possible) * 100) if total_possible else 0,
        })

    career = CareerProgress.query.filter_by(user_id=current_user.id).all()
    technical = [p for p in career if p.skill_name in ["Python Fundamentals", "SQL Fundamentals", "Excel", "Aptitude"]]
    communication = [p for p in career if p.skill_name in ["Communication Skills", "Interview Readiness"]]

    plans = MonthlyPlan.query.filter_by(user_id=current_user.id).order_by(MonthlyPlan.created_at.asc()).all()
    monthly_progress = []
    for plan in plans:
        goals = plan.goals.all()
        avg = round(sum(g.current_percentage for g in goals) / len(goals)) if goals else 0
        monthly_progress.append({
            "month": plan.month_name,
            "progress": avg,
        })
    if not monthly_progress:
        monthly_progress = [{"month": "Month 1", "progress": 0}]

    return jsonify({
        "habit_rate": habit_rate,
        "weekly_consistency": weekly_consistency,
        "monthly_progress": monthly_progress,
        "technical_skills": [{"name": p.skill_name, "value": p.percentage} for p in technical],
        "communication_skills": [{"name": p.skill_name, "value": p.percentage} for p in communication],
    })


@api_bp.route("/transformation-plan", methods=["GET"])
@login_required
def get_transformation_plan():
    progress = PlanProgress.query.filter_by(user_id=current_user.id).all()
    progress_map = {p.day_number: p for p in progress}

    plan = []
    completed_count = 0
    for day_data in TRANSFORMATION_PLAN:
        p = progress_map.get(day_data["day"])
        is_completed = p.completed if p else False
        if is_completed:
            completed_count += 1
        plan.append({
            "day": day_data["day"],
            "title": day_data["title"],
            "tasks": day_data["tasks"],
            "completed": is_completed,
            "notes": p.notes if p else "",
        })

    return jsonify({
        "plan": plan,
        "completed_count": completed_count,
        "total_days": len(TRANSFORMATION_PLAN),
        "percentage": round((completed_count / len(TRANSFORMATION_PLAN)) * 100),
    })


@api_bp.route("/transformation-plan", methods=["POST"])
@login_required
def update_transformation_plan():
    data = request.get_json()
    day_number = data.get("day")
    completed = data.get("completed", False)
    notes = data.get("notes", "")

    progress = PlanProgress.query.filter_by(user_id=current_user.id, day_number=day_number).first()
    if progress:
        progress.completed = completed
        progress.notes = notes

    db.session.commit()

    completed_count = PlanProgress.query.filter_by(user_id=current_user.id, completed=True).count()
    return jsonify({
        "success": True,
        "completed_count": completed_count,
        "percentage": round((completed_count / len(TRANSFORMATION_PLAN)) * 100),
    })
