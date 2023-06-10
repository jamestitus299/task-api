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

        title = data.get("title")
        description = data.get("description")
        dueDate = datetime.fromisoformat(data.get("endDate"))
    # Form data    
    elif (
        request.headers["Content-Type"] == "application/x-www-form-urlencoded"
    ):  
        title = request.form.get("taskTitle")
        description = request.form.get("taskDescription")
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

    tasks = taskCollection.find({}, {"title":1, "description":1, "deadline":1})
    # print(tasks)
    return jsonify(
        [
            {
                "title" : task["title"],
                "description" : task["description"],
                "dueDate" : str(task["deadline"]),
            }
            for task in tasks
        ]
    )














