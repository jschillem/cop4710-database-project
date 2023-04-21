import os
import urllib.request
import json
import sys
from io import StringIO

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
    old_stdout = sys.stdout                   # Redirect stdout to a buffer
    sys.stdout = mystdout = StringIO()
    scraper = MetaCriticScraper(url)    # prints will be captured in the buffer
    sys.stdout = old_stdout                   # Restore stdout

    if len(mystdout.getvalue()) == 0:
        print(f"No data found on {game}.")
    # print(len(mystdout.getvalue()))              # Print if neccesary
    return scraper


#     print("URL: " + scraper.game['url'])
#     print("Image: " + scraper.game['image'])
#     print("Title: " + scraper.game['title'])
#     print("Description: " + scraper.game['description'])
#     print("Platform: " + scraper.game['platform'])
#     print("Publisher: " + scraper.game['publisher'])
#     print("Release Date: " + scraper.game['release_date'])
#     print("Critic Score: " + scraper.game['critic_score'] + "/" + scraper.game['critic_outof'] + " (" + scraper.game['critic_count'] + " critics)")
#     print("User Score: " + scraper.game['user_score'] + " (" + scraper.game['user_count'] + " users)")
#     print("Developer: " + scraper.game['developer'])
#     print("Genre: " + scraper.game['genre'])
#     print("Rating: " + scraper.game['rating'])


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



f = open('games.json')
data = json.load(f)
for k, v in data.items():
    k = k.replace(":","").replace("'","").replace(".", "")\
            .replace("(", "").replace(")", "").replace(" ", "-").strip().lower()

    for console in v:
            if console in platforms:
                scraper = get_data(k, platforms[console])
                break
            else:
                print(f"{console} is not a valid platform")


#
# consoles = set()
# for game in data:
#     consoles.update(data[game])
#
# print(consoles)
# f.close()

