import requests
from bs4 import BeautifulSoup
from MetaCriticScraper import MetaCriticScraper
import json
import time

consoles = set()
games = dict()


def process_row(row, game_dict, console_set):
    cells = row.find_all("td")
    game_name = str(cells[2].contents[1].contents[0]).strip()
    game_link = cells[2].contents[1].get('href')
    print(game_name + ': ' + game_link)
    # parse the game page for consoles
    game_response = requests.get(game_link)
    if game_response.status_code == 429:
        retry_time = response.headers['Retry-After'] + 50
        time.sleep(retry_time / 1000)
        response = requests.get(vgchartz_url)

    game_soup = BeautifulSoup(game_response.content, 'html.parser')
    game_info_box = game_soup.find("div", {"id": "gameGenInfoBox"})
    if game_info_box == None:
        return
    versions = game_info_box.find(string="Other Versions")
    if versions == None:
        return
    platforms = versions.find_parent().find_next_sibling()
    for platform in platforms.find_all('a'):
        print ("\t" + str(platform.string).strip())
        console_set.add(str(platform.string).strip())
        if game_name in game_dict:
            game_dict[game_name].append(str(platform.string).strip())
        else:
            game_dict[game_name] = list()
            game_dict[game_name].append(str(platform.string).strip())

    game_response.close()

for x in range(1, 15):
    print("\n\n")
    print(f"PAGE {x}")
    vgchartz_url = f"https://www.vgchartz.com/games/games.php?page={x}&results=100&console=All&order=TotalShipped&ownership=Both&direction=DESC&showtotalsales=0&shownasales=0&showpalsales=0&showjapansales=0&showothersales=0&showpublisher=0&showdeveloper=0&showreleasedate=0&showlastupdate=0&showvgchartzscore=0&showcriticscore=0&showuserscore=0&showshipped=0&showmultiplat=Yes"
    response = requests.get(vgchartz_url)
    if response.status_code == 429:
        retry_time = response.headers['Retry-After'] + 50
        time.sleep(retry_time / 1000)
        response = requests.get(vgchartz_url)

    soup = BeautifulSoup(response.content, 'html.parser')


    general_body = soup.find("div", {"id": "generalBody"})
    table = general_body.find("table")
    rows = table.find_all("tr")[3:]
    for row in rows:
        process_row(row, games, consoles)

    response.close()

print("Printing games:\n\n")
for game in games:
    print('"' + game + '": ', end='')
    for console in games[game]:
        if len(games[game]) == 1:
            print(console, end='')
        else:
            print(console, end=', ')
    print()

print("Consoles: ", end = '')
print(consoles)

with open("games.json", "w") as outfile:
    json.dump(games, outfile, sort_keys=True, indent=4)

with open("consoles.json", "w") as outfile:
    json.dump(list(consoles), outfile)


