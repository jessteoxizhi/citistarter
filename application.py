import os
import requests
from flask import Flask, jsonify, session, abort, render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['JSON_SORT_KEYS'] = False
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=["GET", "POST"])
def index():
    """Handles signup"""

    # POST - user signup for an account
    if request.method == "POST":

        # Signup Error - user is already loggedin
        if session.get("this_user") is not None:
            return render_template("index.html", alert_user="loggedin", loggedin=True, username=session["this_user"])

        input_username = request.form.get("username")
        input_password = request.form.get("password_one")

        # Signup - check that username does not exist in database
        if db.execute("SELECT * FROM users WHERE username = :username", {"username": input_username}).rowcount == 0:
            db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                       {"username": input_username, "password": input_password})
            db.commit()
        else:
            return render_template("index.html", alert_user="invalidusername", loggedin=False, username=None)

        return render_template("index.html", alert_user="signedup", loggedin=False, username=None)

    # GET - load empty signup page form
    if session.get("this_user") is not None:
        return render_template("index.html", alert_user=None, loggedin=True, username=session["this_user"])
    else:
        return render_template("index.html", alert_user=None, loggedin=False, username=None)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Handles login"""

    # POST - user login to account
    if request.method == "POST":

        # Login Error - user is already loggedin
        if session.get("this_user") is not None:
            return render_template("login.html", alert_user="loggedin", loggedin=True, username=session["this_user"])

        input_username = request.form.get("username")
        input_password = request.form.get("password")

        # Login - check that the username exists in database
        user = db.execute("SELECT * FROM users WHERE username = :username", {"username": input_username}).fetchone()
        if user is None:
            return render_template("login.html", alert_user="invalidusername", loggedin=False, username=None)
        else:
            # check that the input_password is correct according to database
            password = user.password
            if input_password != password:
                return render_template("login.html", alert_user="invalidpassword", loggedin=False, username=None)
            else:
                # Login the user
                session["this_user"] = user.username
                # Redirect to search page
                return redirect(url_for('search'))

    # GET - load empty login page form
    if session.get("this_user") is not None:
        return render_template("login.html", alert_user=None, loggedin=True, username=session["this_user"])
    else:
        return render_template("login.html", alert_user=None, loggedin=False, username=None)


@app.route("/logout", methods=["GET"])
def logout():
    """Handles logout"""

    # Logout Error - user is not loggedin
    if session.get("this_user") is None:
        return render_template("error.html", type="logout", message="You are not loggedin!")

    # Logout Success - clear the session and logout the current user
    session.clear()
    return render_template("success.html", type="logout", message="Logout successfully.")


@app.route("/search", methods=["GET", "POST"])
def search():
    """Handles search"""

    # Forbidden access - user is not loggedin
    if session.get("this_user") is None:
        abort(403)

    # POST - search by user
    if request.method == "POST":
        input_name = request.form.get("name")
        input_year_founded = request.form.get("year_founded")
        input_state = request.form.get("state")

        # Search Invalid - all 3 empty search fields
        if not input_name and not input_year_founded and not input_state:
            return render_template("search.html", search="emptyfield", companies=None, loggedin=True,
                                   username=session["this_user"])

        # Prefix and Suffix the '%'
        # Use upper to make case-insensitive
        input_name = '%' + input_name.upper() + '%'
        input_year_founded = '%' + input_year_founded.upper() + '%'
        input_state = '%' + input_state.upper() + '%'

        # Search - get the search results from database
        companies = db.execute(
            "SELECT * FROM companies WHERE (UPPER(name) LIKE :name AND UPPER(year_founded) LIKE :year_founded AND UPPER(state) LIKE :state)",
            {"name": input_name, "year_founded": input_year_founded, "state": input_state}).fetchall()

        # Return the search results
        return render_template("search.html", search="valid", companies=companies, loggedin=True,
                               username=session["this_user"])

    # GET - redirected from login and load empty search page form
    return render_template("search.html", search=None, companies=None, loggedin=True,
                           username=session["this_user"])


def get_users_reviews(company_id):
    """
    Get users reviews from the database
    Returns reviews, users_rating_count and users_ratings
    """
    reviews = db.execute("SELECT * FROM reviews WHERE company_id = :company_id", {"company_id": company_id}).fetchall()
    users_rating = 0
    users_rating_count = 0
    if reviews:
        sum = 0
        for review in reviews:
            sum += review.rating
        users_rating_count = len(reviews)
        users_rating = round(sum / users_rating_count, 2)
    return reviews, users_rating_count, users_rating


@app.route("/company/<string:company_id>", methods=["GET", "POST"])
def company(company_id):
    """
    Display 1) company info and 2) users reviews
    Also allow this_user to submit reviews
    """

    # Forbidden - user is not loggedin
    if session.get("this_user") is None:
        abort(403)

    # company - get the company from database
    company = db.execute("SELECT * FROM companies WHERE company_id = :company_id",
                         {"company_id": company_id}).fetchone()
    if company is None:
        return render_template("error.html", type="company", message="The company does not exist!")

    # POST - this_user uploads his review!!!
    if request.method == "POST":

        # Review Fail - reject if user has already reviewed
        if db.execute("SELECT * FROM reviews WHERE username = :username AND company_id = :company_id",
                      {"username": session["this_user"], "company_id": company_id}).rowcount != 0:
            # Fetch users ratings from database
            reviews, users_rating_count, users_rating = get_users_reviews(company_id)
            return render_template("company.html", loggedin=True, username=session["this_user"],
                                   alert_user="review_fail", company=company, reviewed=True, reviews=reviews,
                                   users_rating=users_rating, users_rating_count=users_rating_count)

        input_rating = request.form.get("this_rating")
        input_text = request.form.get("this_text")

        # Review Success - add this_user review to the database
        db.execute(
            "INSERT INTO reviews (username, company_id, rating, text) VALUES (:username, :company_id, :rating, :text)",
            {"username": session["this_user"], "company_id": company_id, "rating": input_rating, "text": input_text})
        db.commit()

        # Fetch users ratings from database
        reviews, users_rating_count, users_rating = get_users_reviews(company_id)
        return render_template("company.html", loggedin=True, username=session["this_user"],
                               alert_user="review_success", company=company, reviewed=True, reviews=reviews,
                               users_rating=users_rating, users_rating_count=users_rating_count)

    # Check if this_user has reviewed this company
    reviewed = False
    if db.execute("SELECT * FROM reviews WHERE username = :username AND company_id = :company_id",
                  {"username": session["this_user"], "company_id": company.company_id}).rowcount != 0:
        reviewed = True

    # Fetch users ratings from database
    reviews, users_rating_count, users_rating = get_users_reviews(company_id)
    return render_template("company.html", loggedin=True, username=session["this_user"], company=company,
                           reviewed=reviewed, reviews=reviews, users_rating=users_rating,
                           users_rating_count=users_rating_count)


# Return api request
@app.route("/api/<string:company_id>")
def company_api(company_id):
    """Return details about a single company."""
    # example usage: /api/2

    # Make sure company with company_id exists
    company = db.execute(
        "SELECT company_id, name, industry, description, year_founded, employees, state, city, area, revenue, expenses, profit, growth FROM companies WHERE company_id=:company_id",
        {"company_id": company_id}).fetchone()
    if company is None:
        abort(404)  # return 404 not found error

    # Fetch users ratings from database
    reviews, users_rating_count, users_rating = get_users_reviews(company_id)

    # Keep this json format
    return jsonify({
        "company_id": company[0],
        "name": company[1],
        "industry": company[2],
        "state": company[6],
        "city": company[7],
        "area": company[8],
        "revenue": company[9],
        "expenses": company[10],
        "profit": company[11],
        "growth": company[12],
        "review_count": users_rating_count,
        "average_score": users_rating
    })
