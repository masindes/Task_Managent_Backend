from app import app, db
from models import User, Task, TaskStatus, UserRole
from datetime import datetime

def seed_database():
    with app.app_context():
        # Drop all existing tables and recreate them
        db.drop_all()
        db.create_all()

        # Create 3 users
        user1 = User(
            username="admin",
            email="admin@example.com",
            name="Admin User",
            role=UserRole.ADMIN
        )
        user1.set_password("admin123")  

        user2 = User(
            username="user1",
            email="user1@example.com",
            name="Regular User 1",
            role=UserRole.USER
        )
        user2.set_password("user123") 

        user3 = User(
            username="user2",
            email="user2@example.com",
            name="Regular User 2",
            role=UserRole.USER
        )
        user3.set_password("user456") 

        db.session.add(user1)
        db.session.add(user2)
        db.session.add(user3)
        db.session.commit()

        # Create 3 tasks
        task1 = Task(
            title="Complete project report",
            description="Finish the final project report and submit it by the deadline.",
            due_date=datetime(2023, 12, 15),
            status=TaskStatus.PENDING,
            user_id=user1.id
        )

        task2 = Task(
            title="Prepare presentation",
            description="Prepare slides for the project presentation.",
            due_date=datetime(2023, 12, 10),
            status=TaskStatus.IN_PROGRESS,
            user_id=user2.id
        )

        task3 = Task(
            title="Review code",
            description="Review and merge pull requests for the project.",
            due_date=datetime(2023, 12, 5),
            status=TaskStatus.COMPLETED,
            user_id=user3.id
        )

        db.session.add(task1)
        db.session.add(task2)
        db.session.add(task3)
        db.session.commit()

        print("Database seeded successfully!")

if __name__ == "__main__":
    seed_database()