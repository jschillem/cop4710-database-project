import requests
from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3 as sql
from populate import get_data, db_insert
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
    sql_name = ""

    def fetch(sql_sort, sql_genre):
        try:
            cur.execute(f'''
                            SELECT games.id, games.name, games.release_date, games.game_score, games.cover_img, developers.name AS developer_name
                            FROM games
                            JOIN developed_by ON games.id = developed_by.game
                            JOIN developers ON developed_by.developer = developers.id
                            {sql_name}
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
        
    name = request.args.get('name')
    if name:
        sql_name = f"WHERE LOWER(games.name) LIKE '%{name}%'"

    o = fetch(sql_sort, sql_genre)

    try:
        cur.execute("SELECT data FROM characteristics;");
        genres = cur.fetchall()
    except:
        print("Error")

    con.close()
    return render_template('showGames.html', overdue=o, genres=genres)

@app.route('/recommend', methods=['GET', 'POST'])
def recommend_game():
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

            score_a = cur.execute(f'''SELECT id, game_score FROM games WHERE name = '{selection_a}';''').fetchone()
            name_scores[selection_a] = score_a[1]
            score_b = cur.execute(f'''SELECT id, game_score FROM games WHERE name = '{selection_b}';''').fetchone()
            name_scores[selection_b] = score_b[1]
            score_c = cur.execute(f'''SELECT id, game_score FROM games WHERE name = '{selection_c}';''').fetchone()
            name_scores[selection_c] = score_c[1]
            print(score_a[0], score_b[0], score_c[0])

            # get platforms
            cur.execute(f'''SELECT platforms.full_name
                            FROM supported_on
                            JOIN platforms ON supported_on.platform = platforms.name
                            WHERE supported_on.game IN {score_a[0], score_b[0], score_c[0]};''')
            platforms = tuple(set([row[0] for row in cur.fetchall()]))

            # Avg scoring of the 3 games
            avg_score = (score_a[1] + score_b[1] + score_c[1]) / 3

            # Highest scoring game for genre selection
            highest_score_name = max(name_scores.items(), key=lambda x: x[1])[0]

            joined_table = '''SELECT characteristics.data FROM games
                                    JOIN developed_by ON games.id = developed_by.game
                                    JOIN developers ON developed_by.developer = developers.id
                                    JOIN game_has ON games.id = game_has.id
                                    JOIN characteristics ON characteristics.data = game_has.characteristic'''

            highest_score_genre = cur.execute(f'''{joined_table} WHERE games.name = \'{highest_score_name}\' ''').fetchone()[0]
            # print(highest_score_name)
            # print(highest_score_genre)
            # print(avg_score)

            # Find closest publisher match that has game of genre
            # Make sure the game ISNT one of the 3
            # Abs value used to get closest match
            cur.execute(f'''
                            SELECT games.id, publisher, AVG(game_score) AS avg_score
                            FROM games
                            WHERE publisher IN (SELECT DISTINCT publisher FROM ({joined_table} WHERE characteristics.data = '{highest_score_genre}') )
                            AND games.name NOT IN ('{selection_a}', '{selection_b}', '{selection_c}')
                            GROUP BY publisher
                            ORDER BY ABS(avg_score - {avg_score}) LIMIT 1;''')

            closest_game = cur.fetchone()
            # print(closest_game)
            entry_id = closest_game[0]
            # Make sure the game is on one of the consoles of the 3 games
            # None case

        except:
            print("Error")

        return redirect(f'/entry/{entry_id}', 302)


    con.close()

@app.route('/entry/<int:entry_id>', methods=['GET'])
def entry(entry_id):
    conn = sql.connect('videogame.db')
    cur = conn.cursor()

    cur.execute(f'''SELECT games.cover_img, games.name,  games.age_rating, games.game_score, developers.name, games.publisher, games.release_date, characteristics.data, games.description, games.id
                    FROM games
                    JOIN developed_by ON games.id = developed_by.game
                    JOIN developers ON developed_by.developer = developers.id 
                    JOIN game_has ON games.id = game_has.id
                    JOIN characteristics ON characteristics.data = game_has.characteristic
                    WHERE games.id = {entry_id};''')
    entry = cur.fetchone()

    cur.execute(f'''SELECT platforms.full_name
                    FROM supported_on
                    JOIN platforms ON supported_on.platform = platforms.name
                    WHERE supported_on.game = {entry_id};
                    ''')
    platforms = cur.fetchall()

    conn.close()
    return render_template('entry.html', entry=entry, platforms=platforms)

@app.route('/addGame', methods=['GET', 'POST'])
def add_game():
    if request.method == 'GET':
        return render_template('addGame.html')

    if request.method == 'POST':
        con = sql.connect('videogame.db')
        cur = con.cursor()
        link = request.form['link']

        #Use scraper
        if "metacritic.com" in link:
            scraper = get_data(link = link)
            entry = db_insert(con=con, cur=cur, scraper=scraper, console=[link.split('/')[4]])
            con.close()
            # return the new entry
            if entry:
                return redirect(f'/entry/{entry}', 302)
        return redirect('/addGame', 302)


@app.route('/updateGame', methods=['GET', 'POST'])
def update_game():
    if request.method == 'POST':
        game_id = request.form['game_id']
        name = request.form['name']
        description = request.form['description']
        cover_img = request.form['cover_img']
        publisher = request.form['publisher']
        age_rating = request.form['age_rating']
        game_score = request.form['game_score']
        release_date = request.form['release_date']
        developers = request.form.getlist('developers[]')
        characteristics = request.form.getlist('characteristics[]')
        platforms = request.form.getlist('platforms[]')

        # Update game information in games table
        conn = sql.connect('videogame.db')
        c = conn.cursor()
        c.execute("""
            UPDATE games SET name=?, description=?, cover_img=?, publisher=?, age_rating=?, game_score=?, release_date=?
            WHERE id=?
        """, (name, description, cover_img, publisher, age_rating, game_score, release_date, game_id))
        conn.commit()

        # Update relationships in game_has table
        c.execute("DELETE FROM game_has WHERE id=?", (game_id,))
        for characteristic in characteristics:
            c.execute("INSERT INTO game_has (id, characteristic) VALUES (?, ?)", (game_id, characteristic))
        conn.commit()

        # Update relationships in developed_by table
        c.execute("DELETE FROM developed_by WHERE game=?", (game_id,))
        for developer in developers:
            c.execute("INSERT INTO developed_by (game, developer) VALUES (?, ?)", (game_id, developer))
        conn.commit()

        # Update relationships in supported_on table
        c.execute("DELETE FROM supported_on WHERE game=?", (game_id,))
        for platform in platforms:
            c.execute("INSERT INTO supported_on (game, platform) VALUES (?, ?)", (game_id, platform))
        conn.commit()

        conn.close()

        return redirect(f'/entry/{game_id}', 302)

    else:
        game_id = request.args.get('game_id')
        conn = sql.connect('videogame.db')
        c = conn.cursor()

        # Fetch game information from games table
        c.execute("SELECT * FROM games WHERE id=?", (game_id,))
        game = c.fetchone()
        print(game)

        # Fetch developers, characteristics, and platforms information from respective tables
        c.execute("SELECT * FROM developers ORDER BY name")
        allDevelopers = c.fetchall()

        c.execute('SELECT developer FROM developed_by WHERE game = ?', (game_id,))
        gameDev = c.fetchone()

        c.execute("SELECT * FROM characteristics")
        allCharacteristics = c.fetchall()

        c.execute('SELECT characteristic FROM game_has WHERE id = ?', (game_id,))
        gameChar = c.fetchone()
        gameChar = gameChar[0]
        print(gameChar)

        c.execute("SELECT * FROM platforms")
        allPlatforms = c.fetchall()

        c.execute('SELECT platform FROM supported_on WHERE game = ?', (game_id,))
        gamePlatforms = c.fetchall()

        conn.close()

        return render_template('updateGame.html', game=game, developers=allDevelopers,
                               gameDev=gameDev, characteristics=allCharacteristics,
                               gameChar=gameChar, platforms=allPlatforms,
                               gamePlatforms=gamePlatforms)

@app.route('/delete_game/<int:game_id>', methods=['POST'])
def delete_game(game_id):
    conn = sql.connect('videogame.db')
    c = conn.cursor()

    # Delete the game from games table
    c.execute("DELETE FROM games WHERE id = ?", (game_id,))

    # Delete the game from supported_on table
    c.execute("DELETE FROM supported_on WHERE game = ?", (game_id,))

    # Delete the game from game_has table
    c.execute("DELETE FROM game_has WHERE id = ?", (game_id,))

    conn.commit()
    conn.close()

    return redirect(url_for('show_games'))

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
