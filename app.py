import sqlite3
import os
from sqlite3 import Error

from flask import Flask, flash, jsonify, redirect, render_template, request, session, current_app, g, url_for
from flask_session import Session
from tempfile import mkdtemp
from flask.cli import with_appcontext
from db import sql_connection, sql_insert, sql_fetch
from helpers import login_required
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import datetime

# Upload folder addiotional read
# https://stackoverflow.com/questions/42128484/flask-how-to-get-uploads-folder-path
# https://www.zabana.me/notes/flask-tutorial-upload-files-amazon-s3?fbclid=IwAR2QRIi9bETlqISe__e3lfI58f-7NdHP59RnRnSaaO27hypy37IfyeliEbc
# https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/#an-easier-solution
# https://flask.palletsprojects.com/en/1.1.x/tutorial/views/?highlight=session%20clear
UPLOAD_FILES = "/Users/dotdj/PycharmProjects/flaskProject/static/uploads"
background = "comic2.png"

app = Flask(__name__)

# CONFIGURATION
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config['DEBUG'] = True
app.config['FLASK_ENV'] = 'development'

app.config["IMAGE_UPLOADS"] = UPLOAD_FILES
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF", "NEF"]
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 # The limit is 2 MB
# Error when uploading a too large file explanation an be find here
# https://www.reddit.com/r/flask/comments/8768zv/issue_with_setting_max_content_length_for_file/

# FUNCTIONS
def allowed_image(filename):
    if not "." in filename:
        return False
    ext = filename.rsplit(".", 1)[1]
    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False


# connection to the db
# I used this one!
#https://likegeeks.com/python-sqlite3-tutorial/
sql_connection()

# Make sure API key is set?

# HOMEPAGE
@app.route("/")
@login_required
def index():
    #https://docs.python-guide.org/scenarios/imaging/
    #https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/

    list_of_filenames = {}
    list_of_filenames = os.listdir(UPLOAD_FILES)
    print(list_of_filenames[1])

    return render_template("index.html", filenames = list_of_filenames)

# LOOK AT THIS
# https://pythonise.com/series/learning-flask/flask-uploading-files
# UPLOAD SECTION
@app.route("/upload", methods=["GET", "POST"])
def upload_image():
    if request.method == "POST":
        # verify if the request contains files
        if request.files: 
            
            image = request.files["image"]
                
            if image.filename == "":
                print("No filename")
                #return redirect(request.url)
                return render_template("sorry.html")
                
            if allowed_image(image.filename):
                filename = secure_filename(image.filename)
                
                image.save(os.path.join(app.config["IMAGE_UPLOADS"], image.filename))
                print("image saved")
                #return redirect(request.url)
                return redirect("/")
            else:
                print("That file extension is not allowed")
                #return redirect(request.url)
                return render_template("sorry.html")
    return render_template("upload.html")


# REGISTER, LOGIN, LOGOUT
# The register page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        # change the error messages
        if not request.form.get("username"):
            return render_template("sorry.html")

        if not request.form.get("password"):
            return render_template("sorry.html")

        if not request.form.get("password2"):
            return render_template("sorry.html")

        if request.form.get("password") != request.form.get("password2"):
            return render_template("sorry.html")

        # make an entry into db
        con = sqlite3.connect('users.db')
        current_date = datetime.datetime.today()
        entities = (request.form.get("username"), generate_password_hash(request.form.get("password2")), current_date)
        sql_insert(con, entities)

        return render_template("/login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    if request.method == "GET":
        return render_template("login.html")
    else:
        if not request.form.get("username"):
            return render_template("sorry.html")

        if not request.form.get("password"):
            return render_template("sorry.html")

        # check the db for the user.
        con = sqlite3.connect('users.db')
        answer, id = sql_fetch(con, request.form.get("username"), request.form.get("password"))

        # Ensure username exists and password is correct
        if answer == False:
            # Forget any user_id
            session.clear()
            flash("Invalid username/password!")
            return render_template("login.html")
        else:
            # Remember which user has logged in
            session["user_id"] = id
            return redirect("/")

@app.route("/logout")
@login_required
def logout():
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

# ERRORS
@app.route("/sorry")
def sorry():
    return render_template("sorry.html")

#if __name__ == '__main__':
   # app.run()
