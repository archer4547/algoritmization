# Memory game by Mykhailo Kucheriavenko

# Imports
from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from random import randint, choice
from string import ascii_letters, ascii_lowercase, digits

# Web application
app = Flask(__name__)

# Application configurations
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Database
db = SQL("sqlite:///memory.db")


# Main page route
@app.route("/")
def index():
    return render_template("index.html")


# Game route
@app.route("/game", methods=["GET", "POST"])
def game():

    # If user tries to join the game using link then redirect to main page
    if request.method == "GET":
        return redirect("/")

    # If user joins game using buttons at the main page then game starts
    else:

        # # # Helping functions # # #

        # Make some basic variables when the game starts
        def begin(elements):
            session["level"] = 1
            session["elements"] = elements
            session["list"] = []

        # Generate values based on difficulty
        def game(amount, diff):
            session["diff"] = diff

            # Random_1-5 begin with 5 symbols / words_1-2 begin with 3 words
            begin_amount_5 = ["random_1", "random_2", "random_3", "random_4", "random_5"]
            begin_amount_3 = ["words_1", "words_2"]

            # If the game only started then add one attempt for the user
            # And if no user detected then do nothing
            if not (session.get("user_id") is None) and amount == 5 and diff in begin_amount_5:
                db.execute(f"UPDATE difficulty_attempts SET {diff} = ? WHERE user_id IS ?",
                           db.execute(f"SELECT {diff} FROM difficulty_attempts WHERE user_id IS ?", session["user_id"])[0][diff] + 1, session["user_id"])
            elif not (session.get("user_id") is None) and amount == 3 and diff in begin_amount_3:
                db.execute(f"UPDATE difficulty_attempts SET {diff} = ? WHERE user_id IS ?",
                           db.execute(f"SELECT {diff} FROM difficulty_attempts WHERE user_id IS ?", session["user_id"])[0][diff] + 1, session["user_id"])

            # Difficulty with only numbers
            if diff == "random_1":
                for i in range(amount):
                    session["list"].append(str(randint(0, 9)))

            # Difficulty with  only lowercase letters
            elif diff == "random_2":
                for i in range(amount):
                    session["list"].append(choice(ascii_lowercase))

            # Difficulty with lowercase letters and numbers
            elif diff == "random_3":
                for i in range(amount):
                    session["list"].append(choice(ascii_lowercase + digits))

            # Difficulty with lowercase and uppercase letters
            elif diff == "random_4":
                for i in range(amount):
                    session["list"].append(choice(ascii_letters))

            # Difficulty with lowercase/uppercase letter and numbers
            elif diff == "random_5":
                for i in range(amount):
                    session["list"].append(choice(ascii_letters + digits))

            # Difficulty with words 5-8 symbols
            elif diff == "words_1":
                limit = db.execute("SELECT id FROM ? ORDER BY id DESC LIMIT 1", session["diff"])[0]["id"]
                for i in range(amount):
                    session["list"].append(db.execute("SELECT word FROM ? WHERE id IS ?", session["diff"], randint(1, limit))[0]["word"] + " ")

            # Difficulty with words 9-12 symbols
            elif diff == "words_2":
                limit = db.execute("SELECT id FROM ? ORDER BY id DESC LIMIT 1", session["diff"])[0]["id"]
                for i in range(amount):
                    session["list"].append(db.execute("SELECT word FROM ? WHERE id IS ?", session["diff"], randint(1, limit))[0]["word"] + " ")

        # # # Main code # # #

        # Lists with difficulties where each level adds 1-3 elements (symbols/words)
        per_lvl_1 = ["words_1", "words_2"]
        per_lvl_2 = ["random_1", "random_2", "random_3"]
        per_lvl_3 = ["random_4", "random_5"]

        # Run the "begin" functioon based on the difficulty
        if request.form.get("random_1") or request.form.get("random_2") or request.form.get("random_3") or request.form.get("random_4") or request.form.get("random_5"):
            begin(5)
        elif request.form.get("words_1") or request.form.get("words_2"):
            begin(3)

        # Generate elements for the game for the first time
        if request.form.get("random_1"):
            game(5, "random_1")
        elif request.form.get("random_2"):
            game(5, "random_2")
        elif request.form.get("random_3"):
            game(5, "random_3")
        elif request.form.get("random_4"):
            game(5, "random_4")
        elif request.form.get("random_5"):
            game(5, "random_5")
        elif request.form.get("words_1"):
            game(3, "words_1")
        elif request.form.get("words_2"):
            game(3, "words_2")

        # If user presses "Main menu" after losing
        elif request.form.get("menu"):
            return redirect("/")

        # Checking user's answer
        # All the words are with spaces at the end so there are two correct checks
        elif request.form.get("check") == "".join(session["list"]) or request.form.get("check") + " " == "".join(session["list"]):

            # Changes user's max level if it is bigger then level that was completed
            # If no user detected do nothing
            if not (session.get("user_id") is None) and session["level"] > db.execute(f"SELECT {session['diff']} FROM difficulty_max WHERE user_id IS ?", session["user_id"])[0][session["diff"]]:
                db.execute(f"UPDATE difficulty_max SET {session['diff']} = ? WHERE user_id IS ?", session["level"], session["user_id"])

            # Increment level
            session["level"] += 1

            # Increment element amount and generate one more element

            if session["diff"] in per_lvl_1:
                session["elements"] += 1
                game(1, session["diff"])

            elif session["diff"] in per_lvl_2:
                session["elements"] += 2
                game(2, session["diff"])

            elif session["diff"] in per_lvl_3:
                session["elements"] += 3
                game(3, session["diff"])

        # If check wasn't correct or user tries to do something bad then show "lost" template
        else:
            return render_template("game.html", content="lost")

    # Generate game
    return render_template("game.html", time=10)


# Account route
@app.route("/account", methods=["GET", "POST"])
def account():

    # If user is not detected redirect to main page
    if session.get("user_id") is None:
        return redirect("/")

    # If user is detected
    else:

        # Generate account template
        if request.method == "GET":
            return render_template("account.html", username=db.execute("SELECT username FROM users WHERE id IS ?", session["user_id"])[0]["username"], about=db.execute("SELECT about FROM users WHERE id IS ?", session["user_id"])[0]["about"])

        # Doing what user wanted
        else:

            # Change password
            if request.form.get("old_pass") or request.form.get("old_pass") or request.form.get("confirm_pass"):
                if not request.form.get("old_pass"):
                    return apology("missing old password")
                elif not request.form.get("new_pass"):
                    return apology("missing new password")
                elif not request.form.get("confirm_pass"):
                    return apology("missing confirmation")
                elif request.form.get("new_pass") != request.form.get("confirm_pass"):
                    return apology("passwords do not match")
                elif not check_password_hash(db.execute("SELECT pass_hash FROM users WHERE id IS ?", session["user_id"])[0]["pass_hash"], request.form.get("old_pass")):
                    return apology("wrong old password")
                else:
                    db.execute("UPDATE users SET pass_hash = ? WHERE id IS ?", generate_password_hash(request.form.get("new_pass")), session["user_id"])
                    return success()

            # Change username
            elif request.form.get("new_username"):
                if not db.execute("SELECT username FROM users WHERE username IS ?", request.form.get("new_username")):
                    db.execute("UPDATE comments SET username = ? WHERE username = ?", request.form.get("new_username"),
                            db.execute("SELECT username FROM users WHERE id IS ?", session["user_id"])[0]["username"])
                    db.execute("UPDATE users SET username = ? WHERE id IS ?", request.form.get("new_username"), session["user_id"])
                    return success()
                else:
                    return apology("username already exists")

            # Add information about user
            elif request.form.get("about_text"):
                db.execute("UPDATE users SET about = ? WHERE id IS ?", request.form.get("about_text"), session["user_id"])
                return redirect("/account")

            # If there are no inputs
            # Or if user tries to do something bad
            else:
                return apology("no inputs")


# Stats route
@app.route("/stats")
def stats():

    # If user is not detected redirect to main page
    if session.get("user_id") is None:
        return redirect("/")

    # If user is detected
    else:

        # Select user's stats
        diff_max = db.execute("SELECT random_1, random_2, random_3, random_4, random_5, words_1, words_2 FROM difficulty_max WHERE user_id IS ?", session["user_id"])
        diff_attempts = db.execute("SELECT random_1, random_2, random_3, random_4, random_5, words_1, words_2 FROM difficulty_attempts WHERE user_id IS ?", session["user_id"])

        # Generate page with stats
        return render_template("stats.html", max=diff_max, attempts=diff_attempts)


# Users route
@app.route("/users", methods=["GET", "POST"])
def users():

    # If user uses link to open "users"
    if request.method == "GET":
        return render_template("users.html")

    # If user typed username
    else:
        # If everything is good
        if request.form.get("username"):

            # If username exists
            if db.execute("SELECT username FROM users WHERE username IS ?", request.form.get("username")):
                diff_max = db.execute("SELECT random_1, random_2, random_3, random_4, random_5, words_1, words_2 FROM difficulty_max WHERE user_id IS ?",
                                      db.execute("SELECT id FROM users WHERE username IS ?", request.form.get("username"))[0]["id"])
                diff_attempts = db.execute("SELECT random_1, random_2, random_3, random_4, random_5, words_1, words_2 FROM difficulty_attempts WHERE user_id IS ?",
                                           db.execute("SELECT id FROM users WHERE username IS ?", request.form.get("username"))[0]["id"])
                about = db.execute("SELECT about FROM users WHERE username IS ?", request.form.get("username"))[0]["about"]
                return render_template("users.html", max=diff_max, attempts=diff_attempts, about=about, username=request.form.get("username"))

            # If username does not exist
            else:
                return apology("user not found")

        # If user tried to do something bad
        else:
            return apology("something went wrong")


# Top route
@app.route("/top", methods=["GET", "POST"])
def top():

    # If user uses link to open "top"
    if request.method == "GET":
        return render_template("top.html")

    # if some buttons where pressed
    else:

        # Difficulties list
        difficulties = ["random_1", "random_2", "random_3", "random_4", "random_5", "words_1", "words_2"]

        # If everything is selected
        if request.form.get("select_category") in ["difficulty_max", "difficulty_attempts"] and request.form.get("select_diff") in difficulties:
            content = db.execute(f"SELECT * FROM {request.form.get('select_category')} ORDER BY {request.form.get('select_diff')} DESC LIMIT 10")
            users = []
            for row in content:
                users.append(db.execute("SELECT username FROM users WHERE id IS ?", row["user_id"])[0]["username"])

        # If something is not selected or user tries to do simething bad
        else:
            return apology("missing something")

        # Generate page with user information
        return render_template("top.html", top=content, users=users, len=len(content))


# Comments route
@app.route("/comments", methods=["GET", "POST"])
def comments():

    # If user is not detected redirect to main page
    if session.get("user_id") is None:
        return redirect("/")

    # If user is detected
    else:

        # if user opens "comments" using link
        if request.method == "GET":
            return render_template("comments.html")

        # If user selected one of difficulties
        else:

            # List of difficulties
            difficulties = ["random_1", "random_2", "random_3", "random_4", "random_5", "words_1", "words_2"]

            # Adding comment
            if request.form.get("add") and request.form.get("difficulty") in difficulties and request.form.get("comment"):
                db.execute("INSERT INTO comments (username, difficulty, comment) VALUES (?, ?, ?)",
                        db.execute("SELECT username FROM users WHERE id IS ?", session["user_id"])[0]["username"], request.form.get("difficulty"), request.form.get("comment"))

            # Editing or deleting comment
            if (request.form.get("edit") or request.form.get("delete")) and request.form.get("difficulty") in difficulties and db.execute("SELECT id FROM comments WHERE comment IS ? AND difficulty IS ? AND username IS ? AND id IS ?", request.form.get("previous_comment"), request.form.get("difficulty"), db.execute("SELECT username FROM users WHERE id IS ?", session["user_id"])[0]["username"], request.form.get("id")):
                if request.form.get("edit") and request.form.get("edited_comment"):
                    db.execute("UPDATE comments SET comment = ? WHERE id IS ?", request.form.get("edited_comment"), request.form.get("id"))
                elif request.form.get("delete"):
                    db.execute("DELETE FROM comments WHERE id IS ?", request.form.get("id"))
                else:
                    return apology("something went wrong")

            # If difficulty exists generate template with that difficulty comments
            if request.form.get("difficulty") in difficulties:
                content = db.execute("SELECT id, username, comment FROM comments WHERE difficulty IS ?", request.form.get("difficulty"))
                username = db.execute("SELECT username FROM users WHERE id IS ?", session["user_id"])[0]["username"]
                return render_template("comments.html", content=content, diff=request.form.get("difficulty"), username=username)

            # If user is doing something bad then return "something went wrong"
            else:
                return apology("something went wrong")


# Regiser route
@app.route("/register", methods=["GET", "POST"])
def register():

    # If user pressed "Regiser"
    if request.method == "POST":

        # Checking if everything is ok
        if not request.form.get("username"):
            return apology("missing username")
        elif db.execute("SELECT username FROM users WHERE username IS ?", request.form.get("username")):
            return apology("username already exists")
        elif len(request.form.get("username")) < 3 or len(request.form.get("username")) > 16:
            return apology("incorrect length")
        elif " " in request.form.get("username"):
            return apology("space detected")
        elif not request.form.get("password"):
            return apology("missing password")
        elif not request.form.get("confirmation"):
            return apology("missing confirmation")
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords are not the same")
        else:

            # Adding user
            db.execute("INSERT INTO users (username, pass_hash) VALUES (?, ?)", request.form.get("username"), generate_password_hash(request.form.get("password")))
            db.execute("INSERT INTO difficulty_max (user_id) VALUES (?)", db.execute("SELECT id FROM users WHERE username IS ?", request.form.get("username"))[0]["id"])
            db.execute("INSERT INTO difficulty_attempts (user_id) VALUES (?)", db.execute("SELECT id FROM users WHERE username IS ?", request.form.get("username"))[0]["id"])

            # After registering redirect to login page
            return redirect("/login")

    # If user uses link to open "Regiser"
    else:
        return render_template("register.html")


# Login route
@app.route("/login", methods=["GET", "POST"])
def login():

    # clear all sessions
    session.clear()

    # If user Pressed "Log in"
    if request.method == "POST":

        # Checking if everything is ok
        if not request.form.get("username"):
            return apology("missing username")
        elif not request.form.get("password"):
            return apology("missing password")
        else:

            # Selecting data from the database using username
            user_data = db.execute("SELECT id, username, pass_hash FROM users WHERE username IS ?", request.form.get("username"))

            # If something is wrong with password/username
            if not user_data or not check_password_hash(user_data[0]["pass_hash"], request.form.get("password")):
                return apology("invalid username and/or password")

            # If everything is good
            else:
                session["user_id"] = user_data[0]["id"]

                # Redirect to main page
                return redirect("/")

    # If user uses link to open "login"
    else:
        return render_template("login.html")


# Logout
@app.route("/logout")
def logout():
    session.clear()
    return render_template("success.html")


# Apology
def apology(text):
    return render_template("apology.html", text=text.upper())


# Success
def success():
    return render_template("success.html")
