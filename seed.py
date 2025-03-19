from app import app, db
from models import Task, TaskStatus
from datetime import datetime

def seed_tasks():
    with app.app_context():
        # Clear existing data
        db.session.query(Task).delete()
        db.session.commit()

        # Add sample tasks
        tasks = [
            Task(
                title="Complete project",
                description="Finish the task management application",
                due_date=datetime(2023, 12, 31),
                status=TaskStatus.IN_PROGRESS
            ),
            Task(
                title="Learn Flask",
                description="Study Flask for backend development",
                due_date=datetime(2023, 11, 15),
                status=TaskStatus.PENDING
            ),
            Task(
                title="Deploy application",
                description="Deploy the app to a cloud platform",
                due_date=datetime(2023, 12, 10),
                status=TaskStatus.COMPLETED
            )
        ]

        db.session.add_all(tasks)
        db.session.commit()
        print("Database seeded successfully!")

if __name__ == "__main__":
    seed_tasks()