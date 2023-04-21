import sqlite3
import os.path

if os.path.isfile("videogame.db"):
    print("File already exists.")
    quit()

conn = sqlite3.connect('videogame.db')

try:
    conn.execute('''
        CREATE TABLE games(
           id             INTEGER,
           name           TEXT NOT NULL,
           description    TEXT NOT NULL,
           cover_img      BLOB,
           publisher      TEXT,
           age_rating     TEXT,
           game_score     INTEGER,
           release_date   TEXT NOT NULL,
           PRIMARY KEY    (id)
        );
    ''')

    conn.execute('''
        CREATE TABLE developers(
           id             INTEGER,
           name           TEXT NOT NULL,
           PRIMARY KEY    (id)
        );
    ''')

    conn.execute('''
        CREATE TABLE platforms(
           name           TEXT PRIMARY KEY,
           full_name      TEXT
        );
    ''')

    conn.execute('''
        CREATE TABLE characteristics(
           data           TEXT PRIMARY KEY
        );
    ''')

    conn.execute('''
        CREATE TABLE game_has(
           id             INTEGER,
           characteristic TEXT,
           PRIMARY KEY    (id, characteristic),
           FOREIGN KEY    (id) REFERENCES games,
           FOREIGN KEY    (characteristic) REFERENCES characteristics
        );
    ''')

    conn.execute('''
        CREATE TABLE developed_by(
           game           INTEGER,
           developer      INTEGER,
           PRIMARY KEY    (game, developer),
           FOREIGN KEY    (game) REFERENCES games,
           FOREIGN KEY    (developer) REFERENCES developers
        );
    ''')

    conn.execute('''
        CREATE TABLE supported_on(
           game           INTEGER,
           platform       TEXT,
           PRIMARY KEY    (game, platform),
           FOREIGN KEY    (game) REFERENCES games,
           FOREIGN KEY    (platform) REFERENCES platforms
        );
    ''')

    print("Tables created successfully.")
except Exception as e:
    print(f"Error: {str(e)}")

conn.close()
