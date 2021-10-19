import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
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
@app.route("/landing")
def landing():
    reviews = mongo.db.reviews.find()
    return render_template("landing.html", reviews=reviews)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if user is registered
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Apologies, user is already registered")
            return redirect(url_for("register"))
        
        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }

        mongo.db.users.insert_one(register)

        # put new user into session cookie

        session["user"] = request.form.get("username").lower()
        flash("Registration successful")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    username = mongo.db.users.find_one(
        {"username":session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for('login'))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome {}".format(
                        request.form.get("username")))
                    return redirect(url_for(
                        "profile", username=session["user"]))
            else:
                flash("Incorrect password")
                return redirect(url_for('login'))
        
        else:
            #username doesn't exist
            flash("username doesn't exist")
            return redirect(url_for('login'))

    return render_template("login.html")


@app.route("/logout")
def logout():
    flash("you habe been logged out")
    session.pop("user")
    return redirect(url_for('login'))


@app.route("/add_review", methods=["GET", "POST"])
def add_review():
    if request.method == "POST":
        review = {
            "album": request.form.get("name"),
            "date": request.form.get("date"),
            "desc": request.form.get("desc"),
            "genre": request.form.get("genre"),
            "location": request.form.get("location"),
            "name": request.form.get("name"),
            "img": request.form.get("image"),
            "created_by": session["user"]
        }
        mongo.db.reviews.insert_one(review)
        flash("Task successfully added")
        return redirect(url_for('add_review'))
    
    return render_template("add_review.html")


@app.route("/update_review/<edit_review>", methods=["GET", "POST"])
def update_review(review_id):
    if request.method == "POST":
        review = {
            "album" : request.form.get("name"),
            "date" : request.form.get("date"),
            "desc" : request.form.get("desc"),
            "genre" : request.form.get("genre"),
            "location" : request.form.get("location"),
            "name" : request.form.get("name"),
            "created_by" : session["user"]
        }

        mongo.db.reviews.update({"_id": ObjectId(review_id)}, submit)
        flash("Review updated successfully")
    review = mongo.db.reviews.find_one({"_id": ObjectId(review_id)})
    return render_template("update_review.html", review=review)


@app.route("/delete_review/<review_id>")
def delete_review(review_id):
    mongo.db.reviews.remove({"_id": ObjectId(review_id)})
    flash("Review removed")
    return redirect(url_for('landing'))


@app.route("/add_to_profile/<review_id>")
def add_to_profile(review_id):
    # Allow user to add any review to their own profile so that
    # they can use it as a sort of wishlist
    mongo.db.reviews.find_one(request.form.get("review"))


@app.route("/manage_reviews")
def manage_reviews():
    return render_template("manage_reviews.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP", "0.0.0.0"),
            port=int(os.environ.get("PORT", "5000")), 
            debug=True)