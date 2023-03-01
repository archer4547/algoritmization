import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from calendar import monthrange


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///birthdays.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":

        # Add the user's entry into the database

        if request.form.get("name") and \
        request.form.get("year").isnumeric() and request.form.get("month").isnumeric() and request.form.get("day").isnumeric() and \
        int(request.form.get("month")) >= 1 and int(request.form.get("month")) <= 12 and \
        int(request.form.get("day")) >= 1 and int(request.form.get("day")) <= monthrange(int(request.form.get("year")), int(request.form.get("month")))[1]:
            db.execute("INSERT INTO birthdays (name, month, day) VALUES (?, ?, ?)", request.form.get("name"), request.form.get("month"), request.form.get("day"))

        if request.form.get("del_name") and request.form.get("del_month") and request.form.get("del_day"):
            db.execute("DELETE FROM birthdays WHERE name=? AND month=? AND day=?", request.form.get("del_name"), request.form.get("del_month"), request.form.get("del_day"))

        return redirect("/")

    else:

        # Display the entries in the database on index.html

        data = db.execute("SELECT name, month, day FROM birthdays")

        return render_template("index.html", data=data)


