import requests
from bs4 import BeautifulSoup
import csv

def get_schedule(team, seasons_ago):
    r = requests.get(team.get('value'))
    chicken_noodle = BeautifulSoup(r.content, 'html.parser')
    seasons = chicken_noodle.find('select', {'class':'tablesm'}).find_all('option')
    new_r = requests.get(seasons[seasons_ago].get('value'))
    return BeautifulSoup(new_r.content, 'html.parser')

def get_pbp(url):
    try:
        url = 'http://'+url.split('www.')[1]
        r = requests.get(url)
        clam_chowder = BeautifulSoup(r.content, 'html.parser')
        href = clam_chowder.find('li', {'class':'sub pbp'}).find('a').get('href')
        
        new_r = requests.get('http://www.espn.com'+href)
        return BeautifulSoup(new_r.content, 'html.parser')
    except AttributeError:
        return None

def homeaway(opp_image, pea):
    """
    Returns True if opponent is away and False if the opponent is at home.
    """
    try:
        logo_info = pea.find('div', {'class':'team away'}).find('div', {'class':'team__content'}).find('div', {'class':'team-container'}).find('div', {'class':'team-info-logo'})
        logo = logo_info.find('div', {'class':'logo'}).find('a').find('img').get('src').split('&')[0]
    except AttributeError:
        logo = None
    if logo == opp_image:
        return True
    else:
        return False

def opponent(broth):
    try:
        opp = broth.find('div', {'class':'game-info'}).contents[-1].split('vs ')[-1]
        if '@' in opp:
            opp = opp[2:]
        return opp
    except AttributeError:
        return ""
    
def find_data(bad):
    try:
        lst = ['', '', 0, 0]
        times = bad.find_all('td', {'class':'time-stamp'})
        scores = bad.find_all('td', {'class':'combined-score'})
        plays = bad.find_all('td', {'class':'game-details'})
        last = 0
        index = 0
        for index in range(int((len(times)*3)/4), len(times)):
            moment = times[index].contents[0]
            if '2:' in moment:
                last = index
        
        index = 0
        for index in range(len(plays)):
            if 'Free Throw' in plays[index].contents[0]:
                lst[2] += 1
                if index > last:
                    lst[3] += 1
        
        lst[0] = scores[last].contents[0]
        lst[1] = scores[-1].contents[0]
        return lst
    except IndexError:
        return ['0 - 0','0 - 0', 0, 0]

def wrap(url, seasons_ago):
    r = requests.get(url)
    minestrone = BeautifulSoup(r.content,'html.parser')    
    teams = minestrone.find('select',{'class':'select-box'}).find_all('option')[1:]
    year = 2018 - seasons_ago
    for team in teams:
        name = '-'.join(team.contents[0].split(' ')).lower()
        with open(name+str(year)+'.csv', 'w') as f:
            
            writer = csv.writer(f)
            writer.writerow(['Opponent', 'Opp Score', 'Team Score', 'Opp Final',
                             'Team Final', 'Free Throws', 'Free Throws Under 2 Minutes'])
            tomato = get_schedule(team, seasons_ago)
            games = tomato.find_all('li', {'class':'score'})
            
            for index in range(len(games)):
                try:
                    gazpacho = get_pbp(games[index].find('a').get('href'))
                    if gazpacho != None:
                        data = find_data(gazpacho)
                    else:
                        data = ['0 - 0', '0 - 0', 0, 0]
                except AttributeError:
                    data = ['0 - 0', '0 - 0', 0, 0]
                two_min_score = data[0]
                final_score = data[1]
                early_free_throws = data[2]
                late_free_throws = data[3]
                two_away = int(two_min_score.split(' - ')[0])
                two_home = int(two_min_score.split(' - ')[1])
                final_away = int(final_score.split(' - ')[0])
                final_home = int(final_score.split(' - ')[1])
                
                try:
                    opp_img = games[index].find('div', {'class':'logo'}).find('img')
                    if opp_img != None:
                        opp_image = opp_img.get('src').split('&')[0]
                    else:
                        opp_image = None
                except AttributeError:
                    opp_image = None
                
                if homeaway(opp_image, gazpacho) == True:
                    writer.writerow([opponent(games[index]), two_away, two_home,
                                     final_away, final_home, early_free_throws,
                                     late_free_throws])
                else:
                    writer.writerow([opponent(games[index]), two_home, two_away,
                                     final_home, final_away, early_free_throws,
                                     late_free_throws])

def main():
    for i in range(1,6):
        wrap('http://www.espn.com/mens-college-basketball/team/schedule/_/id/333/year/2017', i)

if __name__ == '__main__':
    main()
  
    