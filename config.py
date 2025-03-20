import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://task_manager_1p9m_user:TVSt6wBVEg3DDhe98JUOhPQs0qDPjC1W@dpg-cve1qjpc1ekc73ebk5f0-a.oregon-postgres.render.com/task_manager_1p9m')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')