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


@app.route('/recommend', methods=['GET', 'POST'])
def recommend_game():
    '''
    Publishers will have a score
    Avg of all their games

    Take 3 games ppl choose
    And avg their scores

    If they all have same genre
    recommend that genre obviously
    Or recommend genre of the highest rated of the 3 games

    Find a publisher with that avg score and
    If they have game of genre recommend highest scored
    If they don’t
    Next publisher

    Must be on one of the consoles of the recommended games
    '''


    con = sql.connect('videogame.db')
    cur = con.cursor()

    if request.method == 'GET':
        cur.execute("SELECT name FROM games");
        games = cur.fetchall()
        games = [game[0] for game in games]
        return render_template('recommendGame.html', games=games)

    if request.method == 'POST':
        try:

            name_scores = {}
            selection_a = request.form['selection_a']
            selection_b = request.form['selection_b']
            selection_c = request.form['selection_c']

            score_a = cur.execute(f'''SELECT game_score FROM games WHERE name = '{selection_a}';''').fetchone()[0]
            name_scores[selection_a] = score_a
            score_b = cur.execute(f'''SELECT game_score FROM games WHERE name = '{selection_b}';''').fetchone()[0]
            name_scores[selection_b] = score_b
            score_c = cur.execute(f'''SELECT game_score FROM games WHERE name = '{selection_c}';''').fetchone()[0]
            name_scores[selection_c] = score_c

            # Avg scoring of the 3 games
            avg_score = (score_a + score_b + score_c) / 3

            # Highest scoring game for genre selection
            highest_score_name = max(name_scores.items(), key=lambda x: x[1])[0]

            joined_table = '''SELECT characteristics.data FROM games
                                    JOIN developed_by ON games.id = developed_by.game
                                    JOIN developers ON developed_by.developer = developers.id
                                    JOIN game_has ON games.id = game_has.id
                                    JOIN characteristics ON characteristics.data = game_has.characteristic'''

            highest_score_genre = cur.execute(f'''{joined_table} WHERE games.name = \'{highest_score_name}\' ''').fetchone()[0]
            print(highest_score_name)
            print(highest_score_genre)
            print(avg_score)

            # Find closest publisher match that has game of genre
            cur.execute(f'''
                            SELECT games.id, publisher, AVG(game_score) AS avg_score
                            FROM games
                            WHERE publisher IN (SELECT DISTINCT publisher FROM ({joined_table} WHERE characteristics.data = '{highest_score_genre}') )
                            GROUP BY publisher
                            ORDER BY ABS(avg_score - {avg_score}) LIMIT 1;''')

            closest_publisher = cur.fetchone()
            print(closest_publisher)
            entry_id = closest_publisher[0]

            # Make sure the game ISNT one of the 3
            # Make sure the game is on one of the consoles of the 3 games
            # Make a selection

        except:
            print("Error")

        return entry(entry_id)


    con.close()



@app.route('/entry/<int:entry_id>', methods=['GET'])
def entry(entry_id):
    conn = sql.connect('videogame.db')
    cur = conn.cursor()

    cur.execute(f'''SELECT games.name FROM games WHERE id = {entry_id};''')
    entry = cur.fetchone()[0]
    print(entry)
    conn.close()
    return render_template('entry.html', entry=entry)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
