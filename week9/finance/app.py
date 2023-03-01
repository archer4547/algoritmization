import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    symbol_dict = db.execute("SELECT DISTINCT(symbol) FROM transactions WHERE user_id IS ?", session["user_id"])

    # Lists that are used in table
    symbols = []
    names = []
    shares = []
    prices = []
    totals = []

    for row in symbol_dict:

        symbol = row["symbol"]
        share = int(db.execute("SELECT SUM(shares) FROM transactions WHERE symbol IS ? AND user_id IS ?",
                    symbol, session["user_id"])[0]["SUM(shares)"])

        if share == 0:
            continue
        else:

            data = lookup(symbol)
            name = data["name"]
            price = data["price"]

            symbols.append(symbol)
            names.append(name)
            shares.append(share)
            prices.append(price)
            totals.append(price * share)

    # User's cash
    cash = db.execute("SELECT cash FROM users where id IS ?", session["user_id"])[0]["cash"]

    # User's + stock's cash
    total = cash + sum(totals)

    return render_template("index.html", symbols=symbols, names=names, shares=shares, prices=prices, totals=totals, cash=cash, total=total, rng=len(symbols))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == "POST":

        if not request.form.get("symbol"):
            return apology("missing symbol")
        elif not lookup(request.form.get("symbol")):
            return apology("symbol does not exist")
        elif not request.form.get("shares"):
            return apology("missing number of shares")
        elif not request.form.get("shares").isnumeric():
            return apology("incorrect shares")
        else:
            stock_info = lookup(request.form.get("symbol"))
            stock_price = stock_info["price"]
            stock_total = stock_price * int(request.form.get("shares"))
            user_cash = db.execute("SELECT cash FROM users WHERE id IS ?", session["user_id"])[0]["cash"]

            if user_cash - stock_total >= 0:
                db.execute("UPDATE users SET cash = ? WHERE id = ?", user_cash - stock_total, session["user_id"])
                db.execute("INSERT INTO transactions (user_id, symbol, name, price, shares, time) VALUES (?, ?, ?, ?, ?, ?)",
                           session["user_id"], stock_info["symbol"], stock_info["name"], stock_info["price"], request.form.get("shares"), datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
                return redirect("/")
            else:
                return apology("can't afford")
    else:

        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    return render_template("history.html", data=db.execute("SELECT symbol, shares, price, time FROM transactions WHERE user_id IS ? ORDER BY transaction_id DESC", session["user_id"]))


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if request.method == "POST":

        if not request.form.get("symbol"):
            return apology("missing symbol")
        elif lookup(request.form.get("symbol")):
            return render_template("quoted.html", data=lookup(request.form.get("symbol")))
        else:
            return apology("invalid symbol")

    else:

        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        if not request.form.get("username"):
            return apology("must provide username")
        elif db.execute("SELECT username FROM users WHERE username IS ?", request.form.get("username")):
            return apology("username already exists")
        elif not request.form.get("password"):
            return apology("must provide password")
        elif not request.form.get("confirmation"):
            return apology("missing password confirmation")
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match")
        else:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)",
                       request.form.get("username"), generate_password_hash(request.form.get("password")))

        return redirect("/register")

    else:

        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    if request.method == "POST":

        if request.form.get("symbol") == "Symbol":
            return apology("select a symbol")
        elif not request.form.get("shares") or not request.form.get("shares").isnumeric():
            return apology("incorrect shares")
        elif int(request.form.get("shares")) > int(db.execute("SELECT SUM(shares) FROM transactions WHERE symbol IS ? AND user_id IS ?", request.form.get("symbol"), session["user_id"])[0]["SUM(shares)"]):
            return apology("too many shares")
        else:

            stock_info = lookup(request.form.get("symbol"))
            stock_price = stock_info["price"]
            stock_total = stock_price * int(request.form.get("shares"))
            user_cash = db.execute("SELECT cash FROM users WHERE id IS ?", session["user_id"])[0]["cash"]

            db.execute("UPDATE users SET cash = ? WHERE id = ?", user_cash + stock_total, session["user_id"])
            db.execute("INSERT INTO transactions (user_id, symbol, name, price, shares, time) VALUES (?, ?, ?, ?, ?, ?)",
                       session["user_id"], stock_info["symbol"], stock_info["name"], stock_info["price"], -int(request.form.get("shares")), datetime.now().strftime("%Y/%m/%d %H:%M:%S"))

            return redirect("/")

    # Render "sell" form
    else:

        symbol_dict = db.execute("SELECT DISTINCT(symbol) FROM transactions WHERE user_id IS ?", session["user_id"])
        symbols = []

        for row in symbol_dict:
            if int(db.execute("SELECT SUM(shares) FROM transactions WHERE symbol IS ? AND user_id IS ?", row["symbol"], session["user_id"])[0]["SUM(shares)"]) == 0:
                continue
            else:
                symbols.append(row["symbol"])

        return render_template("sell.html", symbols=symbols)


@app.route("/change_pass", methods=["GET", "POST"])
@login_required
def change_pass():
    """Change user's password"""

    if request.method == "POST":

        if not request.form.get("previous_pass"):
            return apology("missing previous password")
        elif not request.form.get("new_pass"):
            return apology("missing new password")
        elif not request.form.get("new_pass_confirmation"):
            return apology("missing password confirmation")
        elif request.form.get("new_pass") != request.form.get("new_pass_confirmation"):
            return apology("passwords do not match")
        elif not request.form.get("change_confirmation") or request.form.get("change_confirmation") != "yes":
            return apology("have to confirm")
        elif not check_password_hash(db.execute("SELECT hash FROM users WHERE id = ?", session["user_id"])[0]["hash"], request.form.get("previous_pass")):
            return apology("invalid previous password")
        else:

            db.execute("UPDATE users SET hash = ? WHERE id = ?",
                       generate_password_hash(request.form.get("new_pass")), session["user_id"])

            return redirect("/")

    else:

        return render_template("change_pass.html")


@app.route("/balance", methods=["GET", "POST"])
@login_required
def balance():
    """Change user's balance"""

    if request.method == "POST":

        # Shows balance
        if request.form.get("balance"):
            cash = db.execute("SELECT cash FROM users WHERE id IS ?", session["user_id"])[0]["cash"]
            return render_template("balance.html", content="balance", cash=cash)

        # Showswithdraw form
        elif request.form.get("withdraw"):
            return render_template("balance.html", content="withdraw")

        # Shows deposit form
        elif request.form.get("deposit"):
            return render_template("balance.html", content="deposit")

        # Shows transactions history
        elif request.form.get("history"):
            return render_template("balance.html", content="history", data=db.execute("SELECT type, amount, card, time FROM balance WHERE user_id IS ? ORDER BY transaction_id DESC", session["user_id"]))

        # Withdraw money
        elif request.form.get("w_amount") or request.form.get("w_card") or request.form.get("w_confirmation"):

            if not request.form.get("w_amount"):
                return apology("missing amount")
            elif not request.form.get("w_amount").isnumeric():
                return apology("incorrect amount")
            elif int(request.form.get("w_amount")) > db.execute("SELECT cash FROM users WHERE id IS ?", session["user_id"])[0]["cash"]:
                return apology("not enough cash")
            elif not request.form.get("w_card"):
                return apology("missing card")
            elif not request.form.get("w_card").isnumeric():
                return apology("incorrect card")
            elif not request.form.get("w_confirmation") or request.form.get("w_confirmation") != "yes":
                return apology("have to confirm")
            else:

                amount = int(request.form.get("w_amount"))
                user_cash = db.execute("SELECT cash FROM users WHERE id IS ?", session["user_id"])[0]["cash"]

                db.execute("UPDATE users SET cash = ? WHERE id = ?", user_cash - amount, session["user_id"])
                db.execute("INSERT INTO balance (user_id, type, amount, card, time) VALUES (?, ?, ?, ?, ?)",
                           session["user_id"], "Withdraw", amount, request.form.get("w_card"), datetime.now().strftime("%Y/%m/%d %H:%M:%S"))

                return render_template("balance.html", content="succes")

        # Deposit money
        elif request.form.get("d_amount") or request.form.get("d_card") or request.form.get("d_confirmation"):

            if not request.form.get("d_amount"):
                return apology("missing amount")
            elif not request.form.get("d_amount").isnumeric():
                return apology("incorrect amount")
            elif not request.form.get("d_card"):
                return apology("missing card")
            elif not request.form.get("d_card").isnumeric():
                return apology("incorrect card")
            elif not request.form.get("d_confirmation") or request.form.get("d_confirmation") != "yes":
                return apology("have to confirm")
            else:

                amount = int(request.form.get("d_amount"))
                user_cash = db.execute("SELECT cash FROM users WHERE id IS ?", session["user_id"])[0]["cash"]

                db.execute("UPDATE users SET cash = ? WHERE id = ?", user_cash + amount, session["user_id"])
                db.execute("INSERT INTO balance (user_id, type, amount, card, time) VALUES (?, ?, ?, ?, ?)",
                           session["user_id"], "Deposit", amount, request.form.get("d_card"), datetime.now().strftime("%Y/%m/%d %H:%M:%S"))

                return render_template("balance.html", content="succes")

        else:
            return apology("no inputs")

    else:

        return render_template("balance.html")