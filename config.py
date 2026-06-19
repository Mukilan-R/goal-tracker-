import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "career-growth-dev-secret-key-change-in-production")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_PORT = os.environ.get("MYSQL_PORT", "3306")
    MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "career_tracker")

    USE_SQLITE = os.environ.get("USE_SQLITE", "true").lower() == "true"

    if USE_SQLITE:
        SQLALCHEMY_DATABASE_URI = "sqlite:///career_tracker.db"
    else:
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
            f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
        )
