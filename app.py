import os
from flask import (Flask, render_template, redirect, request, flash,
                    session, url_for)
from bson.objectid import ObjectId
from flask_pymongo import PyMongo
if os.path.exists("env.py"):
    import env.py


app = Flask(__name__)

app.config["MONGO_URI"]= os.environ.get("MONGO_URI")
app.config["MONGODB_NAME"]= os.environ.get("MONGODB_NAME")
app.config["SECRET_KEY"]= os.environ.get("SECRET_KEY")

mongo= PyMongo(app)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")), 
        debug=True)

@app.route("/")
@app.route("/landing")
def landing():
    return render_template("landing.html")