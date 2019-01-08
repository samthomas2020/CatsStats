import requests
from bs4 import BeautifulSoup
import csv
"""
Shot data project.
"""
class Shot:
    def __init__(self, made, shooter, team, #position, 
                 location, assister, quarter):
        """
        -player is a Player class object
        -made is a string, either 'made' or 'missed'
        -location is a list showing how far from the basket with basket location
        being [0,0]
        -assister is a Player class object
        """
        self.made = made
        self.shooter = shooter
        self.team = team
        #self.position = position
        self.location = location
        self.assister = assister
        self.quarter = quarter
        
    def update_time(self, time):
        """
        Works for college. Update for pros.
        """
        if self.quarter == 1:
            minutes = int(time.split(':')[0])
            minutes += 20
            seconds = time.split(':')[1]
            self.time = str(minutes + ':' + seconds)
        else:
            self.time = time

def find_shot_chart(soup):
    return soup.find('div', {'class':'shot-chart'})

def find_shots_away(chart, team):
    """
    Returns a list of Shot objects that correspond to every shot taken by the
    away team.
    """    
    shot_data = chart.find('ul', {'class':'shots away-team'})
    shots = shot_data.find_all('li')
    shots_list = []
    
    for shot in shots:
        made = shot.get('class')[0]
        shooter = shot.get('data-text').split(' '+ made)[0]
        poo = shot.get('style').split(';')
        x = shot.get('style').split(';')[-3].split(':')[1].split('%')[0]
        y = shot.get('style').split(';')[-2].split(':')[1].split('%')[0]
        location = [float(x), float(y)]
        quarter = int(shot.get('data-period'))
        if 'by' in shot.get('data-text'):
            assister = shot.get('data-text').split('by ')[1]
            shots_list.append(Shot(made, shooter, team, assister, location, quarter))
        else:
            shots_list.append(Shot(made, shooter, team, None, location, quarter))
        
    return shots_list

def find_shots_home(chart, team):
    """
    Returns a list of Shot objects that correspond to every shot taken by the
    home team.
    """
    shot_data = chart.find('ul', {'class':'shots home-team'})
    shots = shot_data.find_all('li')
    shots_list = []
    
    for shot in shots:
        made = shot.get('class')[0]
        shooter = shot.get('data-text').split(' '+ made)[0]
        # 100 minus value because shots are displayed on the right side of shot chart
        x = shot.get('style').split(';')[-3].split(':')[1].split('%')[0]
        y = shot.get('style').split(';')[-2].split(':')[1].split('%')[0]
        location = [100 - float(x), float(y)]
        quarter = int(shot.get('data-period'))
        if 'by' in shot.get('data-text'):
            assister = shot.get('data-text').split('by ')[1]
            shots_list.append(Shot(made, shooter, location, assister, quarter))
        else:
            shots_list.append(Shot(made, shooter, team, location, None, quarter))
        
    return shots_list

def find_shot_time(soup, away_shots, home_shots):
    plays = soup.find_all('td', {'class':'game-details'})
    times = soup.find_all('td', {'class':'time-stamp'})
    
    away_index = 0
    home_index = 0
    
    for i in range(len(plays)):
        if 'made' in plays[i].contents[0]:
            if plays[i].contents[0].split(' made')[0] == away_shots[away_index].shooter.name:
                away_shots[away_index].update_time(times[i])
                away_index += 1
            elif plays[i].contents[0].split(' made')[0] == home_shots[home_index].shooter.name:
                home_shots[home_index].update_time(times[i])
                home_index += 1            
        elif 'missed' in plays[i].contents[0]:
            if plays[i].contents[0].split(' missed')[0] == away_shots[away_index].shooter.name:
                away_shots[away_index].update_time(times[i])
                away_index += 1
            elif plays[i].contents[0].split(' missed')[0] == home_shots[home_index].shooter.name:
                home_shots[home_index].update_time(times[i])
                home_index += 1

def wrap(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    chart = soup.find('div', {'class':'shot-chart'})
    away_team = soup.find_all('span',{'class','long-name'})[0].contents[0]
    home_team = soup.find_all('span',{'class','long-name'})[1].contents[0]
    away_shots = find_shots_away(chart, away_team)
    home_shots = find_shots_home(chart, home_team)
    find_shot_time(soup, away_shots, home_shots)
    
    shots = away_shots + home_shots
    
    with open('shot-data.csv', 'w') as f:
        writer = csv.writer(f)
        for shot in shots:
            writer.writerow([shot.team, #shot.position, 
                             shot.shooter, shot.made, shot.location, shot.assister, shot.time])
            
def main():
    url = input('Paste link to play-by-play with shot chart here: ')
    wrap(url)
    
if __name__ == '__main__':
    main()