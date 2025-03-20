from flask import request, jsonify
from datetime import datetime
from app import app, db
from models import User, Task, TaskStatus, UserRole
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity


def validate_task_data(data):
    if not data.get("title") or not data.get("description") or not data.get("due_date"):
        return False
    try:
        datetime.fromisoformat(data["due_date"])
    except ValueError:
        return False
    return True


def is_admin():
    current_user_id = get_jwt_identity()  
    user = User.query.get(int(current_user_id))  
    return user.role == UserRole.ADMIN


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data.get("username") or not data.get("password"):
        return jsonify({"error": "Username and password are required"}), 400

    user = User.query.filter_by(username=data["username"]).first()
    if not user or not user.check_password(data["password"]):
        return jsonify({"error": "Invalid username or password"}), 401

    
    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token}), 200


@app.route("/users", methods=["GET"])
@jwt_required()
def get_users():
    if not is_admin():
        return jsonify({"error": "Admin access required"}), 403

    users = User.query.all()
    return jsonify({"message": "Users retrieved successfully", "data": [user.to_dict() for user in users]}), 200


@app.route("/users/<int:id>", methods=["GET"])
@jwt_required()
def get_user(id):
    current_user_id = get_jwt_identity()
    if int(current_user_id) != id and not is_admin(): 
        return jsonify({"error": "Unauthorized access"}), 403

    user = User.query.get_or_404(id)
    return jsonify({"message": "User retrieved successfully", "data": user.to_dict()}), 200


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
        return jsonify({"message": "User created successfully", "data": new_user.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/users/<int:id>", methods=["PUT"])
@jwt_required()
def update_user(id):
    current_user_id = get_jwt_identity()
    if int(current_user_id) != id and not is_admin(): 
        return jsonify({"error": "Unauthorized access"}), 403

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
            if not is_admin():
                return jsonify({"error": "Admin access required to change role"}), 403
            user.role = UserRole(data["role"])
        if "password" in data:
            user.set_password(data["password"])
        db.session.commit()
        return jsonify({"message": "User updated successfully", "data": user.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/users/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_user(id):
    if not is_admin():
        return jsonify({"error": "Admin access required"}), 403

    user = User.query.get_or_404(id)
    try:
        Task.query.filter_by(user_id=id).delete()  
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted successfully", "data": user.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/tasks", methods=["GET"])
@jwt_required()
def get_tasks():
    current_user_id = get_jwt_identity()
    if is_admin():
        tasks = Task.query.all()
    else:
        tasks = Task.query.filter_by(user_id=int(current_user_id)).all() 
    return jsonify({"message": "Tasks retrieved successfully", "data": [task.to_dict() for task in tasks]}), 200


@app.route("/tasks", methods=["POST"])
@jwt_required()
def create_task():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    if not validate_task_data(data):
        return jsonify({"error": "Invalid task data"}), 400

    try:
        new_task = Task(
            title=data["title"],
            description=data["description"],
            due_date=datetime.fromisoformat(data["due_date"]),
            status=TaskStatus(data.get("status", TaskStatus.PENDING.value)),
            user_id=int(current_user_id) 
        )
        db.session.add(new_task)
        db.session.commit()
        return jsonify({"message": "Task created successfully", "data": new_task.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/tasks/<int:id>", methods=["PUT"])
@jwt_required()
def update_task(id):
    task = Task.query.get_or_404(id)
    current_user_id = get_jwt_identity()

    if task.user_id != int(current_user_id) and not is_admin(): 
        return jsonify({"error": "Unauthorized access"}), 403

    data = request.get_json()
    if not validate_task_data(data):
        return jsonify({"error": "Invalid task data"}), 400

    try:
        task.title = data["title"]
        task.description = data["description"]
        task.due_date = datetime.fromisoformat(data["due_date"])
        task.status = TaskStatus(data.get("status", task.status.value))
        if is_admin() and "user_id" in data:
            task.user_id = data["user_id"]
        db.session.commit()
        return jsonify({"message": "Task updated successfully", "data": task.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/tasks/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_task(id):
    task = Task.query.get_or_404(id)
    current_user_id = get_jwt_identity()

    if task.user_id != int(current_user_id) and not is_admin():  
        return jsonify({"error": "Unauthorized access"}), 403

    try:
        db.session.delete(task)
        db.session.commit()
        return jsonify({"message": "Task deleted successfully", "data": task.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/tasks/<int:id>/complete", methods=["PATCH"])
@jwt_required()
def mark_task_completed(id):
    task = Task.query.get_or_404(id)
    current_user_id = get_jwt_identity()

    if task.user_id != int(current_user_id) and not is_admin(): 
        return jsonify({"error": "Unauthorized access"}), 403

    try:
        task.status = TaskStatus.COMPLETED
        db.session.commit()
        return jsonify({"message": "Task marked as completed", "data": task.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500