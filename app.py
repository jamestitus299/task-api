import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request, abort, render_template
from pymongo import MongoClient
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from bson.objectid import InvalidId
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from models.task import Task

load_dotenv()
app = Flask(__name__)
app.debug = True

# MongoDb configuration
mongo_client = MongoClient(os.environ.get("MONGODB_CONNECTION_URL"))
db = mongo_client["Tasks"]
taskCollection = db["tasks"]

# 1. / endpoint -- TaskApi home page
@app.route("/")
def home():
    return render_template("index.html")

# 2. /task/new endpoint -- to create a new task
@app.route("/task/new", methods=["POST"])
def newTask():
    # JSON data
    if request.headers["Content-Type"] == "application/json":  
        data = request.get_json()

        if data is None:
            abort(400, "Invalid request body. JSON data expected.")

        title = data.get("title").strip()
        description = data.get("description").strip()
        dueDate = datetime.fromisoformat(data.get("endDate"))
    # Form data    
    elif (
        request.headers["Content-Type"] == "application/x-www-form-urlencoded"
    ):  
        title = request.form.get("taskTitle").strip()
        description = request.form.get("taskDescription").strip()
        dueDate= request.form.get("endDate")

        if (
            title == ""
            or description == ""
            or dueDate == ""
        ):
            abort(400, "Invalid request body. Missing Data.")

        dueDate = datetime.fromisoformat(dueDate)
        today = datetime.now()
        if dueDate < today:
            abort(400, "Duedate should be a date following today.")
    # invalid data
    else:
        abort(400, "Unsupported Data or empty body")

    # Store the task in the MongoDb database
    taskData = Task(title, description, dueDate)
    task = taskCollection.insert_one(taskData.__dict__)
    taskId = str(task.inserted_id)

    return jsonify({"id": taskId}), 201


# 3. /task/all -- retrieve all tasks
@app.route("/task/all", methods=["GET"])
def getTasks():

    tasks = taskCollection.find({})
    # print(tasks)
    return jsonify(
        [
            {
                "id": str(task["_id"]),
                "title" : task["title"],
                "description" : task["description"],
                "dueDate" : str(task["deadline"]),
                "status": task["status"]
            }
            for task in tasks
        ]
    )

# 4. /task/<id>/value -- retrieve a task by its id
@app.route("/task/<string:id>/value", methods=["GET", "POST"])
def getTask(id):
    try:
        task = taskCollection.find_one({"_id": ObjectId(id)})

        if not task:
            abort(404, "No task found")

        return jsonify(
                {
                    "id": str(task["_id"]),
                    "title" : task["title"],
                    "description" : task["description"],
                    "dueDate" : str(task["deadline"]),
                    "status": task["status"]
                }
        )
    except InvalidId:
        abort(400, "Invalid TaskId")


# 5. /task/<id>/delete -- delete a task by its id
@app.route("/task/<string:id>/delete", methods=["GET", "POST"])
def deleteTask(id):
    try:
        task = taskCollection.delete_one({"_id": ObjectId(id)})

        if not task:
            abort(404, "No task found")

        return jsonify(
                {
                    "id": id,
                    "message": "Task deleted."
                }
        )
    except InvalidId:
        abort(400, "Invalid TaskId")

# 6. /task/<id>/update -- update a task status
@app.route("/task/<string:id>/update", methods=["GET", "POST"])
def updateTask(id):
    try:
        prevTask = taskCollection.find_one({"_id": ObjectId(id)})
        prevTaskStatus = prevTask["status"]
        task = taskCollection.update_one({"_id": ObjectId(id)}, {"$set": {"status": not prevTaskStatus}})

        if not task:
            abort(404, "No task found")

        return jsonify(
                {
                    "id": id,
                    "message": "Task status updated."
                }
        )
    except InvalidId:
        abort(400, "Invalid TaskId")





if __name__ == "__main__":
    app.run()

