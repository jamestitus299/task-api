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

# Api home page -- documentation
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/task/new", methods=["POST"])
def newTask():
    if request.headers["Content-Type"] == "application/json":  # JSON data
        data = request.get_json()

        if data is None:
            abort(400, "Invalid request body. JSON data expected.")

        title = data.get("title")
        description = data.get("description")
        dueDate = datetime.fromisoformat(data.get("endDate"))
    elif (
        request.headers["Content-Type"] == "application/x-www-form-urlencoded"
    ):  
        # Form data
        title = request.form.get("taskTitle")
        description = request.form.get("taskTitle")
        dueDate= request.form.get("endDate")

        if (
            title == ""
            or description == ""
            or dueDate == ""
        ):
            abort(400, "Invalid request body. Missing Data.")

        dueDate = datetime.fromisoformat(dueDate)

    else:
        abort(400, "Unsupported Data Type or empty body")

    today = datetime.now()

    if dueDate < today:
        abort(400, "End date must be a date after the start date")


    # Store the Quiz in the MongoDb database
    taskData = Task(title, description, dueDate)
    task = taskCollection.insert_one(taskData.__dict__)
    taskId = str(task.inserted_id)

    return jsonify({"id": taskId}), 201














