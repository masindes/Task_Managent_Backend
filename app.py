from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from enum import Enum
import os

# Initialize Flask app
app = Flask(__name__)

# Database configuration for SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///task_management.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy and Flask-Migrate
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Enum for task status
class TaskStatus(Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    tasks = db.relationship('Task', backref='user', lazy=True)  

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "tasks": [task.to_dict() for task in self.tasks] 
        }

# Task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum(TaskStatus), nullable=False, default=TaskStatus.PENDING)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date.isoformat(),
            "status": self.status.value,
            "user_id": self.user_id  
        }

# Helper function to validate task data
def validate_task_data(data):
    if not data.get("title") or not data.get("description") or not data.get("due_date"):
        return False
    try:
        datetime.fromisoformat(data["due_date"])
    except ValueError:
        return False
    return True

# Routes
@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify({
        "message": "Users retrieved successfully",
        "data": [user.to_dict() for user in users]
    }), 200

@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    if not data.get("username") or not data.get("email"):
        return jsonify({"error": "Username and email are required"}), 400

    try:
        new_user = User(
            username=data["username"],
            email=data["email"]
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({
            "message": "User created successfully",
            "data": new_user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/tasks", methods=["GET"])
def get_tasks():
    tasks = Task.query.all()
    return jsonify({
        "message": "Tasks retrieved successfully",
        "data": [task.to_dict() for task in tasks]
    }), 200

@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    if not validate_task_data(data):
        return jsonify({"error": "Invalid task data"}), 400

    try:
        new_task = Task(
            title=data["title"],
            description=data["description"],
            due_date=datetime.fromisoformat(data["due_date"]),
            status=TaskStatus(data.get("status", TaskStatus.PENDING.value)),
            user_id=data.get("user_id") 
        )
        db.session.add(new_task)
        db.session.commit()
        return jsonify({
            "message": "Task created successfully",
            "data": new_task.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/tasks/<int:id>", methods=["PUT"])
def update_task(id):
    task = Task.query.get_or_404(id)

    data = request.get_json()
    if not validate_task_data(data):
        return jsonify({"error": "Invalid task data"}), 400

    try:
        task.title = data["title"]
        task.description = data["description"]
        task.due_date = datetime.fromisoformat(data["due_date"])
        task.status = TaskStatus(data.get("status", task.status.value))
        task.user_id = data.get("user_id", task.user_id)  
        db.session.commit()
        return jsonify({
            "message": "Task updated successfully",
            "data": task.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/tasks/<int:id>", methods=["DELETE"])
def delete_task(id):
    task = Task.query.get_or_404(id)

    try:
        db.session.delete(task)
        db.session.commit()
        return jsonify({
            "message": "Task deleted successfully",
            "data": task.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/tasks/<int:id>/complete", methods=["PATCH"])
def mark_task_completed(id):
    task = Task.query.get_or_404(id)

    try:
        task.status = TaskStatus.COMPLETED
        db.session.commit()
        return jsonify({
            "message": "Task marked as completed",
            "data": task.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

# Run the application
if __name__ == "__main__":
    app.run(debug=True)