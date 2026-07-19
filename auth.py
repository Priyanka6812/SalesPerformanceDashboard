from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from database import db

auth = Blueprint("auth", __name__)


# ------------------------
# Login
# ------------------------
@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            session["user_id"] = user.id
            session["username"] = user.username

            flash("Login Successful", "success")

            return redirect(url_for("dashboard.dashboard"))

        flash("Invalid Email or Password", "danger")

    return render_template("login.html")


# ------------------------
# Register
# ------------------------
@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user:

            flash("Email Already Exists", "warning")

            return redirect(url_for("auth.register"))

        hashed_password = generate_password_hash(password)

        new_user = User(
            username=username,
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration Successful", "success")

        return redirect(url_for("auth.login"))

    return render_template("login.html")


# ------------------------
# Logout
# ------------------------
@auth.route("/logout")
def logout():

    session.clear()

    flash("Logged Out Successfully", "info")

    return redirect(url_for("auth.login"))