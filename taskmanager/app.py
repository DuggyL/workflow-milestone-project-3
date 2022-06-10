import os

from flask import (Flask, flash, render_template, redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)

@app.route("/")
@app.route("/display_tasks")
def display_tasks():
    tasks = list(mongo.db.tasks.find())
    return render_template("tasks.html", tasks = tasks)

@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Sorry, this Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Welcome! Your registration was successful!")
        return redirect(url_for("profile", username=session["user"]))
    return render_template("register.html")

@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exist in database
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password match user input
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome, {}".format(
                        request.form.get("username")))
                    return redirect(
                        url_for("profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Passord") 
                return redirect(url_for("login"))

        else:
            # if username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/profile/<username>", methods = ["GET", "POST"])
def profile(username):
    # grab the session user's name from database
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username = username)

    return redirect(url_for("login"))

@app.route("/logout")
def logout():
    # log out user by remove user's session cookies
    flash("You are logged out")
    session.pop("user")
    return redirect(url_for("login"))

@app.route("/add_task", methods = ["GET", "POST"])
def add_task():
    if request.method == "POST":
        urgent = "on" if request.form.get("urgent") else "off"
        task = {
            "department_name": request.form.get("department_name"),
            "job_title": request.form.get("job_title"),
            "job_no": request.form.get("job_no"),
            "job_description": request.form.get("job_description"),
            "urgent": urgent,
            "delivery_date": request.form.get("delivery_date"),
            "created_by": session["user"]
        }
        mongo.db.tasks.insert_one(task)
        flash("Task Added")
        return redirect(url_for("add_task"))

    departments = mongo.db.departments.find().sort("department_name", 1)
    return render_template("add_task.html", departments = departments)

@app.route("/edit_task/<tasks_id>", methods = ["GET", "POST"])
def edit_task(tasks_id):
    if request.method == "POST":
        urgent = "on" if request.form.get("urgent") else "off"
        submit = {
            "department_name": request.form.get("department_name"),
            "job_title": request.form.get("job_title"),
            "job_no": request.form.get("job_no"),
            "job_description": request.form.get("job_description"),
            "urgent": urgent,
            "delivery_date": request.form.get("delivery_date"),
            "created_by": session["user"]
        }
        mongo.db.tasks.update({"_id": ObjectId(tasks_id)}, submit)
        flash("Task Successfully Updated")

    task = mongo.db.tasks.find_one({"_id": ObjectId(tasks_id)})
    departments = mongo.db.departments.find().sort("department_name", 1)
    return render_template("edit_task.html", task = task, departments = departments)

@app.route("/delete_task/<tasks_id>")
def delete_task(tasks_id):
    mongo.db.tasks.remove({"_id": ObjectId(tasks_id)})
    flash("Task completed")
    return redirect(url_for("display_tasks"))

if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
        port = int(os.environ.get("PORT")),
        debug = True)