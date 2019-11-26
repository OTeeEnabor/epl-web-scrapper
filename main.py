import requests
from bs4 import BeautifulSoup as bs
import numpy as np
import pandas as pd
import re

def remove_digit(string):
    pattern = '[0-9]'
    clean = re.sub(pattern, '', string)
    return clean


base_url = "https://www.premierleague.com/clubs"
#https://fcpython.com/scraping/scraping-premier-league-football-data-python
r = requests.get(base_url)
c = r.content
soup = bs(c,"html.parser")

# find all the links that have the class - indexItem 
# This class is associated with the links to each club in the epl

club_links = soup.find_all("a",{"class":"indexItem"})

# Create a list to store the official link for each team in the English Premier League
team_links = []

team_no = 1
# extract each teams url and store it in the link created above
for item in club_links:
    temp = item.get('href')
    temp = "https://www.premierleague.com" + temp
    temp = temp.replace("overview","squad")
    team_links.append(temp)

# Create empty lists to store player links to each player's overview page and full statistics page

# Create a list to store links to each player's overview page 
players_link_overview = []

# Create a list to store links to each player's full epl statistics page 
player_link_stat = []

#request all the links for each player of each epl team
for i in range(len(team_links)):
    #request each premier league team's link
    squad_page = requests.get(team_links[i])

    squad_page_content = squad_page .content

    team_soup = bs(squad_page_content,"html.parser")

    # from each club page extract all the anchor elements associated with each player in th club
    player_overview = team_soup.find_all("a",{"class":"playerOverviewCard"})
    #
    # Go through all the anchor elements and extract the url 
    for l in range(len(player_overview)):
    # extract the url to the overview page for each player in the team
        players_link_overview.append('https://www.premierleague.com'+ player_overview[l].get('href'))
    

# now for each url to the overview page for each player, edit the link to that it goes to the page that has the statistics 
for k in range(len(players_link_overview)):
# get link for each player comprehendsice stat page in each team in the premier league
    player_link_stat.append(players_link_overview[k].replace("overview","stats"))

