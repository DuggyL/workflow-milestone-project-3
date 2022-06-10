import os

from flask import (Flask, flash, render_template, redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from taskmanager import app, db, mongo
from taskmanager.models import Departments, Users

@app.route("/")
@app.route("/display_tasks")
def display_tasks():
    tasks = list(mongo.db.tasks.find())
    return render_template("tasks.html", tasks = tasks)

@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = Users.query.filter(Users.user_name == \
            request.form.get("username").lower()).all()

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        user = Users(
            user_name = request.form.get("username").lower(),
            password = generate_password_hash(request.form.get("password"))
        )

        db.session.add(user)
        db.session.commit()

        session["user"] = request.form.get("username").lower(),
        flash("Registration Sucessful!")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")

@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exist in database
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            print(request.form.get("username"))
            # ensure hashed password match user input
            if check_password_hash(
                existing_user[0].password, request.form.get("password")):
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

    if "user" in session:
        return render_template("profile.html", username = session["user"])

    return redirect(url_for("login"))

@app.route("/logout")
def logout():
    # log out user by remove user's session cookies
    flash("You are logged out")
    session.pop("user")
    return redirect(url_for("login"))

@app.route("/add_task", methods = ["GET", "POST"])
def add_task():
    if "user" not in session:
        flash("You need to be logged in to add a task")
        return redirect(url_for("display_tasks"))
    
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
        return redirect(url_for("display_tasks"))

    return render_template("display_tasks.html")

@app.route("/edit_task/<tasks_id>", methods = ["GET", "POST"])
def edit_task(tasks_id):

    task = mongo.db.tasks.find_one({"_id": ObjectId(tasks_id)})

    if "user" not in session or session["user"] != task["created_by"]:
        flash("You can only edit your own tasks!")
        return redirect(url_for("display_tasks"))

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

    return render_template("edit_task.html", task = task)

@app.route("/delete_task/<tasks_id>")
def delete_task(tasks_id):

    task = mongo.db.tasks.find_one({"_id": ObjectId(tasks_id)})

    if "user" not in session or session["user"] != task[created_by]:
        flash("You can only delete your own tasks!")
        return redirect(url_for("display_tasks"))

    mongo.db.tasks.remove({"_id": ObjectId(tasks_id)})
    flash("Task completed")
    return redirect(url_for("display_tasks"))