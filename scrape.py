import requests
import pandas as pd
from bs4 import BeautifulSoup
from MetaCriticScraper import MetaCriticScraper


consoles = ["PS2", "PS3","PS4", "PS5", "X360", "XOne", "XS", "PC", "NS"]
games = dict()


for console in consoles:
    for x in range(1, 2):
        print("\n\n")
        print(f"PAGE {x}")
        vgchartz_url = f"https://www.vgchartz.com/games/games.php?page={x}&results=200&console={console}&order=TotalShipped&ownership=Both&direction=DESC&showtotalsales=0&shownasales=0&showpalsales=0&showjapansales=0&showothersales=0&showpublisher=0&showdeveloper=0&showreleasedate=0&showlastupdate=0&showvgchartzscore=0&showcriticscore=0&showuserscore=0&showshipped=0&showmultiplat=Yes"
        response = requests.get(vgchartz_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        general_body = soup.find("div", {"id": "generalBody"})
        table = general_body.find("table")
        rows = table.find_all("tr")[3:]
        for row in rows:
            # Find all cells in the row
            cells = row.find_all("td")
            gameName = str(cells[2].contents[1].contents[0]).strip()
            print('"' + gameName + '"')
            if gameName in games:
                games[gameName].append(console)
            else:
                games[gameName] = list()
                games[gameName].append(console)

for game in games:
    print('"' + game + '": ', end='')
    for console in games[game]:
        if len(games[game]) == 1:
            print(console, end='')
        else:
            print(console, end=', ')
    print()
