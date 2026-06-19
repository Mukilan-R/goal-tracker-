from datetime import date, datetime, timedelta

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login_manager

HABIT_CATEGORIES = [
    "Python Revision",
    "SQL Revision",
    "Excel Practice",
    "Aptitude Practice",
    "English Speaking Practice",
    "GitHub Activity",
    "Interview Preparation",
    "Resume Improvement",
    "Sleep Before 11:30 PM",
]

CAREER_SKILLS = [
    "Python Fundamentals",
    "SQL Fundamentals",
    "Excel",
    "Aptitude",
    "Communication Skills",
    "Interview Readiness",
]

FEAR_CHALLENGES = [
    "Asked a question in class",
    "Spoke in English for 5 minutes",
    "Participated in Group Discussion",
    "Attended Mock Interview",
    "Attended Real Interview",
]

MOOD_OPTIONS = ["Happy", "Normal", "Tired", "Stressed"]

MOTIVATIONAL_QUOTES = [
    "Every expert was once a beginner. Keep learning.",
    "Consistency beats intensity. Show up every day.",
    "Your future self will thank you for today's effort.",
    "Small daily improvements lead to stunning results.",
    "The only bad interview is the one you didn't prepare for.",
    "Code every day, grow every day.",
    "Success is the sum of small efforts repeated daily.",
    "Don't compare your chapter 1 to someone else's chapter 20.",
]

TRANSFORMATION_PLAN = [
    {"day": 1, "title": "Foundation Day", "tasks": ["Set up Python environment", "Write your first Hello World", "Create GitHub account"]},
    {"day": 2, "title": "Python Basics", "tasks": ["Learn variables and data types", "Practice 10 basic exercises", "Push code to GitHub"]},
    {"day": 3, "title": "Control Flow", "tasks": ["Master if-else statements", "Practice loops (for/while)", "Solve 5 loop problems"]},
    {"day": 4, "title": "Functions", "tasks": ["Learn function syntax", "Write 5 reusable functions", "Document your code"]},
    {"day": 5, "title": "Data Structures", "tasks": ["Study lists and dictionaries", "Practice list comprehensions", "Complete a mini project"]},
    {"day": 6, "title": "SQL Introduction", "tasks": ["Install MySQL/SQLite", "Learn SELECT queries", "Practice 10 SELECT exercises"]},
    {"day": 7, "title": "Weekly Review", "tasks": ["Review Python progress", "Review SQL basics", "Plan next week goals"]},
    {"day": 8, "title": "SQL Joins", "tasks": ["Learn INNER and LEFT joins", "Practice join queries", "Solve 5 join problems"]},
    {"day": 9, "title": "SQL Advanced", "tasks": ["Learn GROUP BY and HAVING", "Practice aggregate functions", "Build a sample database"]},
    {"day": 10, "title": "Excel Fundamentals", "tasks": ["Learn basic formulas", "Practice VLOOKUP", "Create a data summary sheet"]},
    {"day": 11, "title": "Aptitude Basics", "tasks": ["Practice 20 math problems", "Learn percentage tricks", "Time yourself on problems"]},
    {"day": 12, "title": "Logical Reasoning", "tasks": ["Solve 15 logic puzzles", "Practice pattern recognition", "Review mistakes"]},
    {"day": 13, "title": "Communication Day", "tasks": ["Speak English for 10 minutes", "Record yourself speaking", "Practice introducing yourself"]},
    {"day": 14, "title": "Weekly Review", "tasks": ["Assess all skill progress", "Update resume bullet points", "Set Week 3 goals"]},
    {"day": 15, "title": "Python OOP", "tasks": ["Learn classes and objects", "Create a simple class project", "Push to GitHub"]},
    {"day": 16, "title": "File Handling", "tasks": ["Learn file read/write in Python", "Process a CSV file", "Automate a small task"]},
    {"day": 17, "title": "Git & GitHub", "tasks": ["Learn git commands", "Create meaningful commits", "Write a good README"]},
    {"day": 18, "title": "Portfolio Project", "tasks": ["Start a portfolio project", "Define project scope", "Complete MVP features"]},
    {"day": 19, "title": "Aptitude Advanced", "tasks": ["Practice time & work problems", "Solve 20 mixed aptitude questions", "Analyze weak areas"]},
    {"day": 20, "title": "Excel Advanced", "tasks": ["Learn pivot tables", "Create charts from data", "Build a dashboard sheet"]},
    {"day": 21, "title": "Weekly Review", "tasks": ["Mid-point assessment", "Update career progress", "Celebrate wins so far"]},
    {"day": 22, "title": "Interview Prep", "tasks": ["Research common Python questions", "Practice 10 coding problems", "Review SQL interview questions"]},
    {"day": 23, "title": "Mock Interview", "tasks": ["Schedule mock interview", "Prepare STAR stories", "Practice behavioral questions"]},
    {"day": 24, "title": "Resume Polish", "tasks": ["Update resume with projects", "Get peer review", "Tailor for target roles"]},
    {"day": 25, "title": "Communication Boost", "tasks": ["Group discussion practice", "Present a technical topic", "Get feedback on communication"]},
    {"day": 26, "title": "Fear Challenge", "tasks": ["Do one thing that scares you", "Ask a question publicly", "Log your challenge"]},
    {"day": 27, "title": "System Design Basics", "tasks": ["Learn basic system concepts", "Study one architecture pattern", "Discuss with peers"]},
    {"day": 28, "title": "Final Project Push", "tasks": ["Complete portfolio project", "Write documentation", "Deploy if possible"]},
    {"day": 29, "title": "Interview Simulation", "tasks": ["Full mock interview session", "Review performance", "Fix weak areas"]},
    {"day": 30, "title": "Transformation Complete", "tasks": ["Final progress review", "Set 90-day goals", "Celebrate your journey!"]},
]


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    habit_entries = db.relationship("HabitEntry", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    career_progress = db.relationship("CareerProgress", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    fear_challenges = db.relationship("FearChallenge", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    weekly_reviews = db.relationship("WeeklyReview", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    monthly_plans = db.relationship("MonthlyPlan", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    monthly_goals = db.relationship("MonthlyGoal", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    mood_entries = db.relationship("MoodEntry", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    plan_progress = db.relationship("PlanProgress", backref="user", lazy="dynamic", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def initialize_defaults(self):
        for skill in CAREER_SKILLS:
            if not CareerProgress.query.filter_by(user_id=self.id, skill_name=skill).first():
                db.session.add(CareerProgress(user_id=self.id, skill_name=skill, percentage=0))

        if not MonthlyPlan.query.filter_by(user_id=self.id, month_name="Month 1").first():
            db.session.add(MonthlyPlan(user_id=self.id, month_name="Month 1"))

        for day_data in TRANSFORMATION_PLAN:
            if not PlanProgress.query.filter_by(user_id=self.id, day_number=day_data["day"]).first():
                db.session.add(PlanProgress(user_id=self.id, day_number=day_data["day"], completed=False))

        db.session.commit()


class HabitEntry(db.Model):
    __tablename__ = "habit_entries"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    entry_date = db.Column(db.Date, nullable=False, default=date.today)
    habit_name = db.Column(db.String(100), nullable=False)
    completed = db.Column(db.Boolean, default=False)

    __table_args__ = (db.UniqueConstraint("user_id", "entry_date", "habit_name"),)


class CareerProgress(db.Model):
    __tablename__ = "career_progress"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    skill_name = db.Column(db.String(100), nullable=False)
    percentage = db.Column(db.Integer, default=0)

    __table_args__ = (db.UniqueConstraint("user_id", "skill_name"),)


class FearChallenge(db.Model):
    __tablename__ = "fear_challenges"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    challenge_type = db.Column(db.String(100), nullable=False)
    completed_date = db.Column(db.Date, nullable=False, default=date.today)
    notes = db.Column(db.Text, default="")


class WeeklyReview(db.Model):
    __tablename__ = "weekly_reviews"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    week_start = db.Column(db.Date, nullable=False)
    wins = db.Column(db.Text, default="")
    mistakes = db.Column(db.Text, default="")
    lessons = db.Column(db.Text, default="")
    goals = db.Column(db.Text, default="")

    __table_args__ = (db.UniqueConstraint("user_id", "week_start"),)


class MonthlyPlan(db.Model):
    __tablename__ = "monthly_plans"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    month_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    goals = db.relationship("MonthlyGoal", backref="plan", lazy="dynamic", cascade="all, delete-orphan")

    __table_args__ = (db.UniqueConstraint("user_id", "month_name"),)


class MonthlyGoal(db.Model):
    __tablename__ = "monthly_goals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey("monthly_plans.id"), nullable=False)
    goal_name = db.Column(db.String(200), nullable=False)
    target_percentage = db.Column(db.Integer, default=100)
    current_percentage = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint("plan_id", "goal_name"),)


class MoodEntry(db.Model):
    __tablename__ = "mood_entries"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    entry_date = db.Column(db.Date, nullable=False, default=date.today)
    mood = db.Column(db.String(20), nullable=False)

    __table_args__ = (db.UniqueConstraint("user_id", "entry_date"),)


class PlanProgress(db.Model):
    __tablename__ = "plan_progress"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    day_number = db.Column(db.Integer, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text, default="")

    __table_args__ = (db.UniqueConstraint("user_id", "day_number"),)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def get_week_start(d=None):
    d = d or date.today()
    return d - timedelta(days=d.weekday())


def calculate_streak(user_id):
    today = date.today()
    current_streak = 0
    check_date = today

    while True:
        entries = HabitEntry.query.filter_by(user_id=user_id, entry_date=check_date).all()
        if not entries:
            if check_date == today:
                check_date -= timedelta(days=1)
                continue
            break

        completed = sum(1 for e in entries if e.completed)
        total = len(HABIT_CATEGORIES)
        if completed >= total * 0.5:
            current_streak += 1
            check_date -= timedelta(days=1)
        else:
            if check_date == today:
                check_date -= timedelta(days=1)
                continue
            break

    all_dates = set()
    streak_dates = {}
    entries_all = HabitEntry.query.filter_by(user_id=user_id).all()
    for e in entries_all:
        all_dates.add(e.entry_date)

    longest = 0
    temp = 0
    sorted_dates = sorted(all_dates)
    for i, d in enumerate(sorted_dates):
        entries = [e for e in entries_all if e.entry_date == d]
        completed = sum(1 for e in entries if e.completed)
        if completed >= len(HABIT_CATEGORIES) * 0.5:
            temp += 1
            longest = max(longest, temp)
        else:
            temp = 0

    return current_streak, longest


def get_daily_score(user_id, target_date=None):
    target_date = target_date or date.today()
    entries = HabitEntry.query.filter_by(user_id=user_id, entry_date=target_date).all()
    completed = sum(1 for e in entries if e.completed)
    total = len(HABIT_CATEGORIES)
    return round((completed / total) * 100) if total else 0


def get_overall_progress(user_id):
    career = CareerProgress.query.filter_by(user_id=user_id).all()
    if not career:
        return 0
    return round(sum(c.percentage for c in career) / len(career))


def get_streak_badge(streak):
    if streak >= 30:
        return {"name": "Legend", "icon": "🏆", "color": "#f59e0b"}
    if streak >= 14:
        return {"name": "Champion", "icon": "🥇", "color": "#eab308"}
    if streak >= 7:
        return {"name": "Warrior", "icon": "⚔️", "color": "#8b5cf6"}
    if streak >= 3:
        return {"name": "Rising Star", "icon": "⭐", "color": "#3b82f6"}
    return {"name": "Beginner", "icon": "🌱", "color": "#22c55e"}
