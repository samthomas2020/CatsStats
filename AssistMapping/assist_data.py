import requests
from bs4 import BeautifulSoup
import csv

def track_game_data(soup, players, assist_array, img):
    plays = soup.find_all('td',{'class':'game-details'})
    logos = soup.find_all('td',{'class':'logo'})
    index = 0
    for play in plays:
        logo = logos[index].find('img').get('src')
        logo = logo.split('/i/')[1].split('&')[0]
        index += 1
        contents = play.contents[0]
        if logo == img and 'Assisted' in contents:
            score = contents.split('. Assisted')[0]
            scorer = score.split(' made')[0]
            assist = contents.split('. Assisted')[1]
            passer = assist.split('by ')[1][:-1]
            if passer in players:
                row = players.index(passer)
                if scorer in players:
                    col = players.index(scorer)
                else:
                    players.append(scorer)
                    lst = []
                    for i in range(len(assist_array)):
                        lst.append(0)
                        assist_array[i].append(0)
                    lst.append(0)
                    assist_array.append(lst)
                    col = len(players) - 1
            else:
                players.append(passer)
                lst = []
                for i in range(len(assist_array)):
                    lst.append(0)
                    assist_array[i].append(0)
                lst.append(0)
                assist_array.append(lst)
                row = len(players) - 1
                if scorer in players:
                    col = players.index(scorer)
                else:
                    players.append(scorer)
                    lst = []
                    for i in range(len(assist_array)):
                        lst.append(0)
                        assist_array[i].append(0)
                    lst.append(0)
                    assist_array.append(lst)                   
                    col = len(players) - 1
            assist_array[row][col] += 1
                    
def season_iterator(url, players, assist_array):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    
    logo = soup.find('span',{'class':'brand-logo'}).find('img').get('src').split('&')[0]
    logo = logo.split('/i/')[1]
    schedule = soup.find('section', {'class':'club-schedule'})
    games = schedule.find_all('li')
    
    for game in games:
        try:
            new_url = 'http://www.espn.com'+game.find('a').get('href')
            new_r = requests.get(new_url)
            new_soup = BeautifulSoup(new_r.content, 'html.parser')
            
            tab = new_soup.find('li', {'class':'sub pbp'})
            href = tab.find('a').get('href')
            
            newest_r = requests.get('http://www.espn.com'+href)
            newest_soup = BeautifulSoup(newest_r.content, 'html.parser')
            
            track_game_data(newest_soup, players, assist_array, logo)
        except AttributeError:
            pass
    
        
def wrap(url):
    players = []
    assist_array = []    
    season_iterator(url, players, assist_array)
    
    with open(url.split('/')[-1]+'-assists.csv', 'w') as f:
        writer = csv.writer(f)
        to_write = [''] + players
        writer.writerow(to_write)
        
        for row in range(len(assist_array)):
            to_write = [players[row]] + assist_array[row]
            writer.writerow(to_write)

def main():
    wrap(input("Paste the url to a team's ESPN clubhouse here: "))
    
if __name__ == "__main__":
    main()