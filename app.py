from flask import Flask, request, jsonify
from datetime import datetime
from models import db, Task, TaskStatus

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/task_management'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

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
@app.route("/tasks", methods=["GET"])
def get_tasks():
    tasks = Task.query.all()
    return jsonify([task.to_dict() for task in tasks]), 200

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
            status=TaskStatus(data.get("status", TaskStatus.PENDING.value))
        )
        db.session.add(new_task)
        db.session.commit()
        return jsonify(new_task.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/tasks/<int:id>", methods=["PUT"])
def update_task(id):
    task = Task.query.get(id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json()
    if not validate_task_data(data):
        return jsonify({"error": "Invalid task data"}), 400

    try:
        task.title = data["title"]
        task.description = data["description"]
        task.due_date = datetime.fromisoformat(data["due_date"])
        task.status = TaskStatus(data.get("status", task.status.value))
        db.session.commit()
        return jsonify(task.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/tasks/<int:id>", methods=["DELETE"])
def delete_task(id):
    task = Task.query.get(id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    try:
        db.session.delete(task)
        db.session.commit()
        return jsonify({"message": "Task deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/tasks/<int:id>/complete", methods=["PATCH"])
def mark_task_completed(id):
    task = Task.query.get(id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    try:
        task.status = TaskStatus.COMPLETED
        db.session.commit()
        return jsonify(task.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Error handler
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(debug=True)