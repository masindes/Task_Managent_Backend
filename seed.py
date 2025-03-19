from app import app, db, User, Task, TaskStatus
from datetime import datetime

def seed_database():
    with app.app_context():
        # Drop all tables and recreate them
        db.drop_all()
        db.create_all()

        # Create users
        user1 = User(username="john_doe", email="john@example.com")
        user2 = User(username="jane_doe", email="jane@example.com")

        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        # Create tasks
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
            description="Review and refactor the codebase for better performance.",
            due_date=datetime(2023, 12, 20),
            status=TaskStatus.PENDING,
            user_id=user1.id
        )

        db.session.add(task1)
        db.session.add(task2)
        db.session.add(task3)
        db.session.commit()

        print("Database seeded successfully!")

if __name__ == "__main__":
    seed_database()