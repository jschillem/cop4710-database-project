import requests
from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3 as sql
import re

descendingName = False
descendingScore = False

app = Flask(__name__)
app.config['SECRET_KEY'] = 'any string works here'

@app.route('/', methods=['GET'])
def show_games():
    global descendingName
    global descendingScore
    con = sql.connect('videogame.db')
    cur = con.cursor()
    sql_sort = "ORDER BY games.game_score DESC;"
    sql_genre = ""

    def fetch(sql_sort, sql_genre):
        try:
            cur.execute(f'''
                            SELECT games.id, games.name, games.release_date, games.game_score, games.cover_img, developers.name AS developer_name
                            FROM games
                            JOIN developed_by ON games.id = developed_by.game
                            JOIN developers ON developed_by.developer = developers.id
                            {sql_genre}
                            {sql_sort}
                        ''')
            overdue = cur.fetchall()
            return overdue
        except:
            print("Error")  # Not found



    sort = request.args.get('sort')
        
    if sort:
        if sort == 'name':
            d = '' if not descendingName else 'DESC'
            descendingName = not descendingName
            sql_sort = f"ORDER BY games.name {d};"
        elif sort == 'score':
            d = '' if not descendingScore else 'DESC'
            descendingScore = not descendingScore
            sql_sort = f"ORDER BY games.game_score {d};"

    genre = request.args.get('genre')
    if genre:
        sql_genre = f'''JOIN game_has ON games.id = game_has.id
                        JOIN characteristics ON characteristics.data = game_has.characteristic
                        WHERE characteristics.data = \'{genre}\''''

    o = fetch(sql_sort, sql_genre)
    try:
        cur.execute("SELECT data FROM characteristics");
        genres = cur.fetchall()
    except:
        print("Error")

    con.close()
    return render_template('showGames.html', overdue=o, genres=genres)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
