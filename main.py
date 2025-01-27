import ast
import os
import json

import sqlite3

import uuid

from flask import Flask, render_template, request, redirect, url_for, flash, session

from werkzeug.security import generate_password_hash, check_password_hash

import smtplib

from email.mime.text import MIMEText

from email.mime.multipart import MIMEMultipart



app = Flask(__name__)

app.secret_key = "dhsbjjdjsjdjsnj1"  # Replace with your own secret key



DATABASE = 'users.db'

RESET_TOKENS = {}



# Helper function to get the database connection

def get_db():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn



# Initialize the database

def init_db():

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute('''

        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT NOT NULL UNIQUE,

            email TEXT NOT NULL UNIQUE,

            password TEXT NOT NULL

        )

    ''')

    conn.commit()

    conn.close()



first_request_done = False



@app.before_request

def before_request():

    global first_request_done

    if not first_request_done:

        first_request_done = True

        startup()



def startup():

    print("Application has started, and the database is being initialized.")

    init_db()





@app.route("/", methods=["GET"])

def home():

    return render_template("home.html")



@app.route("/login", methods=["GET", "POST"])

def login():

    if request.method == "POST":

        email = request.form['email']

        password = request.form['password']

        

        conn = get_db()

        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))

        user = cursor.fetchone()

        

        if user and check_password_hash(user['password'], password):

            return redirect(url_for("index"))

        else:

            flash("Invalid email or password", "danger")

            return render_template("login.html")

    return render_template("login.html")



@app.route("/signup", methods=["GET", "POST"])

def signup():

    if request.method == "POST":

        username = request.form['username']

        email = request.form['email']

        password = request.form['password']

        

        hashed_password = generate_password_hash(password)

        conn = get_db()

        cursor = conn.cursor()

        

        try:

            cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', 

                           (username, email, hashed_password))

            conn.commit()

            return redirect(url_for("login"))

        except sqlite3.IntegrityError:

            flash("Email or username already exists", "danger")

            return render_template("signup.html")

    return render_template("signup.html")



@app.route("/forgot-password", methods=["GET", "POST"])

def forgot_password():

    if request.method == "POST":

        email = request.form['email']

        

        conn = get_db()

        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))

        user = cursor.fetchone()

        

        if user:

            token = str(uuid.uuid4())

            RESET_TOKENS[token] = user['email']

            

            # Send reset email

            sender_email = "hemanth4203@gmail.com"  # Replace with your email

            sender_password = "yqye zeyn odec xrsk"  # Replace with your email password

            smtp_server = "smtp.gmail.com"  # Replace with your email provider's SMTP server

            smtp_port = 587 

            

            reset_link = f"http://127.0.0.1:5000/reset-password?token={token}"

            message = MIMEMultipart()

            message['From'] = sender_email

            message['To'] = email

            message['Subject'] = "Password Reset Request"

            body = f"Click the link to reset your password: {reset_link}"

            message.attach(MIMEText(body, 'plain'))

            

            try:

                with smtplib.SMTP(smtp_server, smtp_port) as server:

                    server.starttls()

                    server.login(sender_email, sender_password)

                    server.sendmail(sender_email, email, message.as_string())

                flash("Password reset instructions sent to your email", "info")

                return render_template("forgot_password.html")

            except Exception as e:

                flash(f"Failed to send email: {str(e)}", "danger")

                return render_template("forgot_password.html")

        else:

            flash("No user found with this email", "danger")

            return render_template("forgot_password.html")

    return render_template("forgot_password.html")



@app.route("/reset-password", methods=["GET", "POST"])

def reset_password():

    token = request.args.get('token')

    email = RESET_TOKENS.get(token)

    

    if not email:

        return render_template("error.html", error="Invalid or expired token")

    

    if request.method == "POST":

        password = request.form['password']

        hashed_password = generate_password_hash(password)

        

        conn = get_db()

        cursor = conn.cursor()

        cursor.execute('UPDATE users SET password = ? WHERE email = ?', (hashed_password, email))

        conn.commit()

        

        RESET_TOKENS.pop(token, None)

        return redirect(url_for("login"))

    

    return render_template("reset_password.html", token=token)



@app.route("/index", methods=["GET"])

def index():

    return render_template("index.html")



@app.route("/fetchLatest", methods=["GET"])

def fetch_latest():

    adminUsername = request.args.get("username")

    adminPassword = request.args.get("password")

    contest_slug = request.args.get("contestSlug")

    

    # Replace with your actual logic to fetch data

    hr = HRMain(adminUsername, adminPassword, contest_slug)

    data = hr.fetchData()

    return render_template("index.html", data=data)



@app.route("/fetchOld", methods=["GET"])

def fetch_old():

    adminUsername = request.args.get("username")

    adminPassword = request.args.get("password")

    contest_slug = request.args.get("contestSlug")

    

    # Replace with your actual logic to fetch old data

    hr = HRMain(adminUsername, adminPassword, contest_slug)

    data = hr.fetchOldData()

    return render_template("userAttempts.html", data=data)



@app.route("/plagiariseCode", methods=["GET"])

def plagiarise_code():

    userData = request.args.get('userData')

    

    try:

        userData = ast.literal_eval(userData)

    except (ValueError, SyntaxError) as e:

        return {"error": f"Invalid userData format: {str(e)}"}

    

    res = plagiariseCodes(userData)

    return render_template("result.html", request=res)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))