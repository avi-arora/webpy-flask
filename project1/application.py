import os, requests
from functools import wraps
from flask import Flask, session, render_template, request, url_for, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

API_KEY = "yeFY55rpiY2HDly04zQbw"
BASE_URL = "https://www.goodreads.com"

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def authorize(f):
    @wraps(f)
    def wrapper(*args, **kargs):
        if session.get("username") != None:
            return f(*args, **kargs)
        else:
            return redirect(url_for("login"))
    return wrapper


@app.route("/")
def index():
    return "Project 1: TODO"


@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/registeruser", methods=["POST"])
def registeruser():
    #extract the fields
    pwd, confPwd = request.form.get("pwd"), request.form.get("confPwd")
    if pwd != confPwd:
        pass
    else:
        uname, email = request.form.get("uname"), request.form.get("email")

        db.execute("INSERT into users(username,email,password) VALUES (:uname,:email,:pwd)",
        {"uname":uname, "email": email, "pwd": pwd})
        try: 
            db.commit()
            responseObj = {"message":"Registered successfully.", "status":"SUCCESS"}
        except Exception:
            responseObj = {"message":"Error,Please try again later.", "status":"ERROR"}
            
        return redirect(url_for("login"))

@app.route("/authenticate", methods=["POST"])
def authenticate():
    uname, pwd = request.form.get("uname"), request.form.get("pwd")
    user = db.execute("SELECT * FROM users WHERE email=:uname AND password=:pwd",{"uname": uname, "pwd": pwd}).fetchone()

    if user: 
        session["username"] = user.username
    
    return redirect(url_for("search"))


@app.route("/search",methods=['GET'])
@authorize
def search():
    query = request.args.get("q")
    searchResult = []
    if query != None:
        searchResult = db.execute("SELECT * FROM Book WHERE \
        (title = :query OR author = :query or isbn = :query) \
         OR (isbn LIKE :exp OR title LIKE :exp OR author LIKE :exp)"
         ,{"query": query, "exp": "%" + query}).fetchall()

    return render_template("search.html", searchResult=searchResult)

@app.route("/book/<string:isbn>")
@authorize
def book(isbn):
    #get book from goodread api
    response = requests.get(BASE_URL + "/book/review_counts.json", params={"isbns":isbn,"key":API_KEY})
    data = response.json()
    return render_template("book.html")

@app.route("/logout")
def logout():
    session.pop("username")
    return redirect(url_for("login"))



