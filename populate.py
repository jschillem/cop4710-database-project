import os
import urllib.request
import json
import sys
from io import StringIO
import sqlite3
import math

# Required file
filename = 'MetaCriticScraper.py'
url = 'https://raw.githubusercontent.com/JaeguKim/Metacritic-Python-API/master/MetaCriticScraper.py'
if not os.path.exists(filename):
    print(f"Downloading {filename} from {url}...")
    urllib.request.urlretrieve(url, filename)
    print(f"{filename} has been downloaded.")
else:
    print(f"{filename} already exists.")

from MetaCriticScraper import MetaCriticScraper



def get_data(game, console):
    url = f'https://www.metacritic.com/game/{console}/{game}'
    print(url)

    # Stifling prints
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()
    scraper = MetaCriticScraper(url)
    sys.stdout = old_stdout

    if len(mystdout.getvalue()) == 0:
        print(f"No data found on {game}.")
        return None
    # print(len(mystdout.getvalue()))              # Print if neccesary
    return scraper


    print("URL: " + scraper.game['url'])
    print("Image: " + scraper.game['image'])
    print("Title: " + scraper.game['title'])
    print("Description: " + scraper.game['description'])
    print("Platform: " + scraper.game['platform'])
    print("Publisher: " + scraper.game['publisher'])
    print("Release Date: " + scraper.game['release_date'])
    print("Critic Score: " + scraper.game['critic_score'] + "/" + scraper.game['critic_outof'] + " (" + scraper.game['critic_count'] + " critics)")
    print("User Score: " + scraper.game['user_score'] + " (" + scraper.game['user_count'] + " users)")
    print("Developer: " + scraper.game['developer'])
    print("Genre: " + scraper.game['genre'])
    print("Rating: " + scraper.game['rating'])


# Only platforms we are using, there is a lot of them.
platforms = {
                       'PS3': 'playstation-3',
                       'X360': 'xbox-360',
                       'PC': 'pc',
                       'WiiU': 'wii-u',
                       '3DS': '3ds',
                       'PSV': 'playstation-vita',
                       'iOS': 'ios',
                       'Wii': 'wii',
                       'DS': 'ds',
                       'PSP': 'psp',
                       'PS2': 'playstation-2',
                       'PS': 'playstation',
                       'XB': 'xbox',
                       'GC': 'gamecube',
                       'GBA': 'game-boy-advance',
                       'DC': 'dreamcast',
                       'PS4': 'playstation-4',
                       'PS5': 'playstation-5',
                       'XOne': 'xbox-one',
                       'XS': 'xbox-series-x',
                       'NS': 'switch'
                       }


platformFull = {
                       'PS3': 'Playstation 3',
                       'X360': 'Xbox 360',
                       'PC': 'PC',
                       'WiiU': 'Wii U',
                       '3DS': '3DS',
                       'PSV': 'Playstation Vita',
                       'iOS': 'iOS',
                       'Wii': 'Wii',
                       'DS': 'DS',
                       'PSP': 'PSP',
                       'PS2': 'Playstation 2',
                       'PS': 'Playstation',
                       'XB': 'Xbox',
                       'GC': 'Gamecube',
                       'GBA': 'Gameboy Advance',
                       'DC': 'Dreamcast',
                       'PS4': 'Playstation 4',
                       'PS5': 'Playstation 5',
                       'XOne': 'Xbox One',
                       'XS': 'Xbox Series X/S',
                       'NS': 'Nintendo Switch'
                       }

conn = sqlite3.connect('videogame.db')
cur = conn.cursor()

# Insert platforms to db
cur.execute("SELECT COUNT(*) FROM platforms")
count_row = cur.fetchone()
print (count_row[0])

if count_row[0] == 0:
    for k, v in platformFull.items():
        cur.execute("INSERT INTO platforms (name, full_name) VALUES (?, ?)", (k, v))

conn.commit()

f = open('games.json')
data = json.load(f)
for k, v in data.items():
    k = k.replace(":","").replace("'","").replace(".", "")\
            .replace("(", "").replace(")", "").replace(" ", "-").strip().lower()

    scraper = None
    for console in v:
            if console in platforms:
                scraper = get_data(k, platforms[console])
                break
            else:
                print(f"{console} is not a valid platform")

    if scraper:
        try:
            # Insert game
            if not scraper.game['critic_score']:
                continue

            cur.execute('''INSERT INTO games 
                            (name, description, cover_img, publisher, age_rating, game_score, release_date)
                            VALUES(?, ?, ?, ?, ?, ?, ?)''',
                            (scraper.game['title'],
                            scraper.game['description'],
                            scraper.game['image'],
                            scraper.game['publisher'],
                            scraper.game['rating'],
                            int(scraper.game['critic_score']),
                            scraper.game['release_date']))
            
            title = scraper.game['title']
            cur.execute(f'SELECT * FROM games WHERE name = "{title}"')
            game_id_row = cur.fetchone()
            game_id = int(game_id_row[0])
            print(str(game_id) + ': ' + scraper.game['title'])

            # Insert characteristic if not already in DB, and then create game_has relationship
            genre = scraper.game['genre']
            cur.execute(f'SELECT * FROM characteristics WHERE data = "{genre}"')
            char_row = cur.fetchone()
            if char_row is None:
                cur.execute("INSERT INTO characteristics (data) VALUES (?)", (scraper.game['genre'],))
            
            cur.execute("INSERT INTO game_has (id, characteristic) VALUES (?, ?)", (game_id, scraper.game['genre']))

            # Insert developer if not already in DB, and then create developed_by relationship
            developer = scraper.game['developer']
            cur.execute(f'SELECT * FROM developers WHERE name = "{developer}"')
            dev_row = cur.fetchone()
            if dev_row is None:
                cur.execute("INSERT INTO developers (name) VALUES (?)", (scraper.game['developer'],))
            
            cur.execute(f'SELECT id FROM developers WHERE name = "{developer}"')
            dev_id_row = cur.fetchone()
            dev_id = int(dev_id_row[0])
            
            cur.execute("INSERT INTO developed_by (game, developer) VALUES (?, ?)", (game_id, dev_id))

            for console in v:
                cur.execute("INSERT INTO supported_on (game, platform) VALUES (?, ?)", (game_id, console))
            
            conn.commit()

        except Exception as e:
            print(f"Error: {str(e)}")
    


#
# consoles = set()
# for game in data:
#     consoles.update(data[game])
#
# print(consoles)

conn.close()
f.close()

