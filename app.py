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


class LoginForm(FlaskForm):
    username = StringField('username: ', validators=[DataRequired()])
    password = StringField('password: ', validators=[DataRequired()])
    submit = SubmitField('Submit')


class SignUpForm(FlaskForm):
    username = StringField('username: ', validators=[DataRequired()])
    password = StringField('password: ', validators=[DataRequired()])
    confirmpassword = StringField('confirmpassword: ', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm()
        if form.validate_on_submit():
            print(form.username.data)
            print(form.password.data)
            try:
                # Fetch form submission
                user = form.username.data
                passw = form.password.data

                con = sql.connect('userData.db')
                cur = con.cursor()

                cur.execute(f"SELECT username FROM users WHERE username ='{user}'")
                if len(cur.fetchall()) == 1:
                    passasbitstring = str.encode(passw)
                    userpass = pbkdf2_hmac('sha256', passasbitstring, b'bad salt' * 2, 100000)

                    cur.execute(f"SELECT password FROM users WHERE username =\"{user}\" AND password =\"{userpass}\"")
                    if len(cur.fetchall()) == 1:
                        print("success")
                        session['loggedInUser'] = user
                        con.close()
                        return render_template('index.html')
                    else:
                        print("Error: Incorrect Password")
                        con.close()
                        return render_template('login.html', form=form)
                else:
                    print("Error: Username not found")
                    con.close()
                    return render_template('login.html', form=form)
                con.commit()

            except:
                con.rollback()
                print("Error")
                return render_template('login.html', form=form)
    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    con = sql.connect('userData.db')
    cur = con.cursor()

    if request.method == 'POST':
        form = SignUpForm()
        if form.validate_on_submit():

            print(form.username.data)
            print(form.password.data)
            print(form.confirmpassword.data)
            try:
                # Fetch form submission
                user = form.username.data
                passw = form.password.data
                conpass = form.confirmpassword.data
                cur.execute(f"SELECT username FROM users WHERE username ='{user}'")
                if len(cur.fetchall()) != 0:
                    print("Username is taken")
                    # con.close()
                    return render_template('signup.html', form=form)
                if passw == conpass:
                    print(user, passw)
                    passasbitstring = str.encode(passw)
                    userpass = pbkdf2_hmac('sha256', passasbitstring, b'bad salt' * 2, 100000)
                    # hash function running user password through sha256 100000 times.
                    print(userpass)
                    cur.execute(f"INSERT INTO users (username, password) VALUES ('{user}',\"{userpass}\")")
                    con.commit()
                    print("success")
                    # con.close()
                    return render_template('signup.html', form=form)

                else:
                    print('passwords must match')
                    # con.close()
                    return render_template('signup.html', form=form)


            except:
                con.rollback()
                print("1 Error")

    return render_template('signup.html', form=form)


@app.route('/showGames', methods=['GET', 'POST'])
def show_games():
    con = sql.connect('videogame.db')
    cur = con.cursor()
    # user = session.get('loggedInUser', None)
    # print(user)

    def fetch():
        try:
            cur.execute("SELECT id, name, release_date, game_score FROM games")
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
