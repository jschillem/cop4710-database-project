import requests
from flask import Flask, render_template, request, session, redirect, url_for
from flask_wtf import FlaskForm
from wtforms.fields import DateField, StringField, TimeField

from wtforms.validators import DataRequired
from wtforms import validators, SubmitField

from hashlib import pbkdf2_hmac

import sqlite3 as sql

app = Flask(__name__)
app.config['SECRET_KEY'] = 'any string works here'

@app.route('/', methods=['GET', 'POST'])
def show_games():
    con = sql.connect('videogame.db')
    cur = con.cursor()

    def fetch():
        try:
            cur.execute('''
                SELECT games.id, games.name, games.release_date, games.game_score, games.cover_img, developers.name AS developer_name
                FROM games
                JOIN developed_by ON games.id = developed_by.game
                JOIN developers ON developed_by.developer = developers.id
                ORDER BY games.game_score DESC;
            ''')
            overdue = cur.fetchall()
            return overdue
        except:
            print("Error")  # Not found

    if request.method == 'POST':

        for getid in request.form.getlist('check'):
            print(getid)

        o = fetch()
        con.close()
        return render_template('showGames.html', overdue=o)

    # con.close()
    o = fetch()
    con.close()
    return render_template('showGames.html', overdue=o)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
