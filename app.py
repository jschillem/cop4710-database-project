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
    sql_filter = "ORDER BY games.game_score DESC;"

    def fetch(sql_filter):
        try:
            print(sql_filter)

            cur.execute(f'''
                            SELECT games.id, games.name, games.release_date, games.game_score, games.cover_img, developers.name AS developer_name
                            FROM games
                            JOIN developed_by ON games.id = developed_by.game
                            JOIN developers ON developed_by.developer = developers.id
                            {sql_filter}
                        ''')
            overdue = cur.fetchall()
            return overdue
        except:
            print("Error")  # Not found

    filter = request.args.get('filter')
        
    if filter:

        if filter == 'name':
            d = '' if not descendingName else 'DESC'
            descendingName = not descendingName
            sql_filter = f"ORDER BY games.name {d};"
        # if filter == 'release':
        #     sql_filter = "ORDER BY games.release_date DESC;"
        if filter == 'score':
            d = '' if not descendingScore else 'DESC'
            descendingScore = not descendingScore
            sql_filter = f"ORDER BY games.game_score {d};"

    # con.close()
    o = fetch(sql_filter)
    con.close()
    return render_template('showGames.html', overdue=o)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
