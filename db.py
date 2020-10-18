import sqlite3
from sqlite3 import Error
from werkzeug.security import check_password_hash, generate_password_hash
from flask import redirect, render_template

def sql_connection():

    try:

        con = sqlite3.connect('users.db', detect_types=sqlite3.PARSE_COLNAMES)

        print("Connection is established: Database is created in memory")

    except Error:

        print(Error)

    finally:

        con.close()


def sql_insert(con, entities):

    cursorObj = con.cursor()

    cursorObj.execute('INSERT INTO users(username, hash, joining_date) VALUES(?, ?, ?)', entities)

    con.commit()

def sql_fetch(con, username, password):

    con.row_factory=sqlite3.Row
    cursorObj = con.cursor()
    #https://docs.python.org/3/library/sqlite3.html

    cursorObj.execute('SELECT * FROM users WHERE username = :username', {"username": username})
    rows = cursorObj.fetchone()
    answer = check_password_hash(rows['hash'], password)

    return answer, rows['id']