from flask import request, jsonify
from datetime import datetime
from app import app, db
from models import User, Task, TaskStatus, UserRole
from werkzeug.security import generate_password_hash


def validate_task_data(data):
    if not data.get("title") or not data.get("description") or not data.get("due_date"):
        return False
    try:
        datetime.fromisoformat(data["due_date"])
    except ValueError:
        return False
    return True


@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify({
        "message": "Users retrieved successfully",
        "data": [user.to_dict() for user in users]
    }), 200

@app.route("/users/<int:id>", methods=["GET"])
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify({
        "message": "User retrieved successfully",
        "data": user.to_dict()
    }), 200

@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    if not data.get("username") or not data.get("email") or not data.get("password") or not data.get("name"):
        return jsonify({"error": "Username, email, password, and name are required"}), 400

    try:
        new_user = User(
            username=data["username"],
            email=data["email"],
            name=data["name"],
            role=UserRole(data.get("role", UserRole.USER.value)) 
        )
        new_user.set_password(data["password"])
        db.session.add(new_user)
        db.session.commit()
        return jsonify({
            "message": "User created successfully",
            "data": new_user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/users/<int:id>", methods=["PUT"])
def update_user(id):
    user = User.query.get_or_404(id)
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        if "username" in data:
            user.username = data["username"]
        if "email" in data:
            user.email = data["email"]
        if "name" in data:
            user.name = data["name"]
        if "role" in data:
            user.role = UserRole(data["role"])
        if "password" in data:
            user.set_password(data["password"]) 

        db.session.commit()
        return jsonify({
            "message": "User updated successfully",
            "data": user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/users/<int:id>", methods=["DELETE"])
def delete_user(id):
    user = User.query.get_or_404(id)

    try:
        
        Task.query.filter_by(user_id=id).delete()
        
    
        db.session.delete(user)
        db.session.commit()
        return jsonify({
            "message": "User deleted successfully",
            "data": user.to_dict()
        }), 200
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


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500