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

"""
The players on the epl official page are grouped into 4 different positions namely Goalkeeper, Defender, Midfielder and Forward. Each of these positions have different statitics associated with them, therefore I will store these statistics seperately
"""
# create lists to store these statistics for each player position
gk_stats = []
df_stats = []
mid_stats = []
fw_stats = [] 

# create  lists to store  each players dictionary by position
gk_sup_dic = []
df_sup_dic = []
mid_sup_dic =[]
fw_sup_dic = []

for player in player_link_stat:
    # request the player statistics page 
    player_stat_page_request = requests.get(player)
    player_stat_page_content = player_stat_page_request.content
    player_stat_page_html = bs(player_stat_page_content,"html.parser")
    # search for the player's position 
    player_position = player_stat_page_html.find_all("div",{"class":"info"})[1].text.strip()

    # create a list to store statistics which were tricky to extract in the previous technique


    col_heading = [] # heading - the statistics name

    col_stat = [] # value associated with the statitstics 

    # get all the name of the statistics associated with this player
    player_stat_heading = player_stat_page_html.select('div.normalStat')

    for heading in range(len(player_stat_heading)):

        value_ = player_stat_page_html.select('div.normalStat span.allStatContainer')[heading].text.strip()

        column = player_stat_page_html.select('div.normalStat span.stat')[heading].text.replace(value_,"").replace(" ","").replace("\n","").replace("\r","")
        
        clean_column = remove_digit(column)

        col_heading.append(clean_column)

        col_stat.append(value_)
    
    #get no of player appearances 
    player_app_stat = player_stat_page_html.select('div.topStat span.allStatContainer')[0].text.strip()
    # add the player's number of appearances to the col_stat
    col_stat.append(player_app_stat)

    # get the column heading for number of appearances
    player_app_heading = player_stat_page_html.select('div.topStat span.stat')[0].text.replace(player_app_stat,"").replace(" ","").replace("\n","").replace("\r","")
    
    # add to col_heading 
    col_heading.append(player_app_heading)

    col_heading.append("Name")

    col_heading.append("Club")

    player_name  = player_stat_page_html.select('div.name')[0].text
    col_stat.append(player_name) 

    # player club - there are some players who do not have the club that they are associated with on their page. use a try and except statement to handle this problem

    try:
        player_club = player_stat_page_html.select('div.info a')[0].text.strip()
        col_stat.append(player_club)

    except:
        player_club = None
        col_stat.append(player_club)

    column_heading = []
    stat=[]

    try:
        print(player_name+" is a "+"Current player is a: "+player_position + " Current team:"+player_club)


    except TypeError as e:
        print(e)
    
    # sort each player by position 

    if player_position == "Goalkeeper":

        #if goalkeeper heading column is empty populate
        if len(gk_stats)==0:

            #populate dictionary
            gk = {}
            for counter in range(len(col_stat)):
                gk[col_heading[counter]] = col_stat[counter]
                #print(col_heading[counter]+": " + col_stat[counter] )
            gk_sup_dic.append(gk)
            gk_stats=[]
    elif player_position == "Defender":
         if len(df_stats)==0:
            #populate dictionary
            df = {}
            for counter in range(len(col_stat)):
                df[col_heading[counter]] = col_stat[counter]
            df_sup_dic.append(gk)
            df_stats=[]

    elif player_position == "Midfielder":
        #if mid heading column is empty populate
         if len(mid_stats)==0:
            #populate dictionary
            md = {}
            for counter in range(len(col_stat)):
                md[col_heading[counter]] = col_stat[counter]
            mid_sup_dic.append(md)
            mid_stats=[]

    elif player_position == "Forward":
        #if goalkeeper heading column is empty populate
         if len(fw_stats)==0:

            #populate dictionary
            fw = {}
            for counter in range(len(col_stat)):
                fw[col_heading[counter]] = col_stat[counter]
            fw_sup_dic.append(fw)
            fw_stats=[]
    else:
        pass 

"""
Create a dataframe that from each of the lists that stores the players into each position and save this data frame into a csv file.

"""
gk_df = pd.DataFrame(gk_sup_dic)
gk_df.to_csv("csv/epl_GK.csv")
defender_df = pd.DataFrame(df_sup_dic)
defender_df.to_csv("csv/epl_def.csv")
mid_df = pd.DataFrame(mid_sup_dic)
mid_df.to_csv("csv/epl_mid.csv")
fw_df = pd.DataFrame(fw_sup_dic)
fw_df.to_csv("csv/epl_fw.csv")

