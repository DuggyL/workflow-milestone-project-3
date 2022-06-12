from flask import Flask, flash, render_template, redirect, request, session, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from taskmanager import app, db, mongo
from taskmanager.models import Customer

@app.route("/")

@app.route("/get_tasks")
def get_tasks():
    tasks = list(mongo.db.tasks.find())
    return render_template("tasks.html", tasks=tasks)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                        session["user"] = request.form.get("username").lower()
                        flash("Welcome, {}".format(
                            request.form.get("username")))
                        return redirect(url_for(
                            "profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # remove user from session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_task", methods=["GET", "POST"])
def add_task():
    if request.method == "POST":
        is_urgent = "on" if request.form.get("urgent") else "off"
        task = {
            "job_title": request.form.get("job_title"),
            "company_name": request.form.get("company_name"),
            "job_description": request.form.get("job_description"),
            "quantity": request.form.get("quantity"),
            "materials": request.form.get("materials"),
            "printing": request.form.get("printing"),
            "finishing": request.form.get("finishing"),
            "delivery": request.form.get("delivery"),
            "delivery_date": request.form.get("delivery_date"),
            "delivery_address": request.form.get("delivery_address"),
            "urgent": is_urgent,
            "created_by": session["user"]
        }
        mongo.db.tasks.insert_one(task)
        flash("Task Successfully Added")
        return redirect(url_for("get_tasks"))

    return render_template("add_task.html")


@app.route("/edit_task/<task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    if request.method == "POST":
        is_urgent = "on" if request.form.get("urgent") else "off"
        submit = {
            "job_title": request.form.get("job_title"),
            "job_description": request.form.get("job_description"),
            "quantity": request.form.get("quantity"),
            "materials": request.form.get("materials"),
            "printing": request.form.get("printing"),
            "finishing": request.form.get("finishing"),
            "delivery": request.form.get("delivery"),
            "delivery_date": request.form.get("delivery_date"),
            "delivery_address": request.form.get("delivery_address"),
            "urgent": is_urgent,
            "created_by": session["user"]
        }
        mongo.db.tasks.replace_one({"_id": ObjectId(task_id)}, submit)
        flash("Task Successfully Updated")
        return redirect(url_for("get_tasks"))

    task = mongo.db.tasks.find_one({"_id": ObjectId(task_id)})
    return render_template("edit_task.html", task=task)


@app.route("/delete_task/<task_id>")
def delete_task(task_id):
    mongo.db.tasks.delete_one({"_id": ObjectId(task_id)})
    flash("Task Successfully Deleted")
    return redirect(url_for("get_tasks"))


@app.route("/add_customer", methods=["GET", "POST"])
def add_customer():
    if request.method == "POST":
        customer = Customer(
            company_name=request.form.get("company_name"),
            customer_name=request.form.get("customer_name"),
            contact_no=request.form.get("contact_no"),
            email=request.form.get("email"),
            address=request.form.get("address"),
        )
        db.session.add(customer)
        db.session.commit()
        return redirect(url_for("get_tasks"))
    return render_template("add_customer.html")