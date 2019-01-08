import requests
from bs4 import BeautifulSoup
import csv
#import xlsxwriter
"""
This is a program that scrapes ESPN's NCAAM standings page to find any team's 
ESPN clubhouse homepage and produces a csv file with the score of each game that
it has participated in with 2 minutes to go in the game. It does so by using the
requests and BeautifulSoup packages to scrape for HTML data and the csv package 
to write to the csv file.
Author: Sam Thomas
"""
def current_season_access_games(url):
    """
    Requires the url to the team's current clubhouse page.
    """
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    schedule = soup.find('section', {'class':'club-schedule'})
    return schedule.find_all('li')

def previous_season_access_games(url):
    """
    Requires the url to the team's previous season schedule page
    """
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    schedule = soup.find_all('li', {'class':'score'})
    return schedule

def opponent(soup):
    opp = soup.find('div', {'class':'game-info'}).contents[-1].split('vs ')[-1]
    if '@' in opp:
        opp = opp[2:]
    return opp

def homeaway(opp_image, soup):
    """
    Returns True if opponent is away and False if the opponent is at home.
    """
    team = soup.find('div', {'class':'team away'})
    content = team.find('div', {'class':'team__content'})
    container = content.find('div', {'class':'team-container'})
    logo_info = container.find('div', {'class':'team-info-logo'})
    try:
        logo = logo_info.find('div', {'class':'logo'}).find('a').find('img').get('src').split('&')[0]
    except AttributeError:
        logo = None
    if logo == opp_image:
        return True
    else:
        return False

def get_pbp(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    tab = soup.find('li', {'class':'sub pbp'})
    a = tab.find('a')
    href = a.get('href')
    
    new_r = requests.get('http://www.espn.com'+href)
    new_soup = BeautifulSoup(new_r.content, 'html.parser')
    return new_soup   

def find_score(soup):
    try:
        lst = ['', '', 0, 0]
        times = soup.find_all('td', {'class':'time-stamp'})
        scores = soup.find_all('td', {'class':'combined-score'})
        plays = soup.find_all('td', {'class':'game-details'})
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
        
def wrap(url): # add book
    games = current_season_access_games(url)
    #games = previous_season_access_games(url)
    with open(url.split('/')[-1]+'.csv', 'w') as f: # if previous year, add '-YYYY' before .csv in the file name
        writer = csv.writer(f)
        writer.writerow(['Opponent', 'Opp Score', 'Team Score', 'Opp Final', 'Team Final', 'Free Throws', 'Free Throws Under 2 Minutes'])   
        # indent everything from here...
        #sheet = book.add_worksheet(url.split('/')[-1][:31])
        #sheet.write_string(0, 0, 'Opponent')
        #sheet.write_string(0, 1, 'Opp Score')
        #sheet.write_string(0, 2, 'Team Score')
        index = 0
        opp_image = None
        href = None
        pbp = None
        two_minute_score = None
        final_score = None
        away = None
        home = None
        while games[index].find('a').get('class')[-1] == '':
        #for i in games:
            opp_img = games[index].find('div', {'class':'logo'}).find('img')
            if opp_img != None:
                opp_image = opp_img.get('src').split('&')[0]
            else:
                opp_image = None
            href = games[index].find('a').get('href')
            try:
                pbp = get_pbp('http://www.espn.com'+href)
                #pbp = get_pbp_previous(href)
                score = find_score(pbp)
                two_minute_score = score[0]
                final_score = score[1]
                early_free_throws = score[2]
                late_free_throws = score[3]
            except AttributeError:
                scores = ['0 - 0', '0 - 0', 0, 0]
            two_away = int(two_minute_score.split(' - ')[0])
            two_home = int(two_minute_score.split(' - ')[1])
            final_away = int(final_score.split(' - ')[0])
            final_home = int(final_score.split(' - ')[1])
            if homeaway(opp_image, pbp) == True:
                writer.writerow([opponent(games[index]), two_away, two_home, final_away, final_home, early_free_throws, late_free_throws])
                #sheet.write_string(index + 1, 0, opponent(games[index]))
                #sheet.write_number(index + 1, 1, away)
                #sheet.write_number(index + 1, 2, home)
            else:
                writer.writerow([opponent(games[index]), two_home, two_away, final_home, final_away, early_free_throws, late_free_throws])
                #sheet.write_string(index + 1, 0, opponent(games[index]))
                #sheet.write_number(index + 1, 1, home)
                #sheet.write_number(index + 1, 2, away)
            index += 1
        # ...to here

def main():
    #book = xlsxwriter.Workbook('two-minute-scores.xlsx')
    r  = requests.get('http://www.espn.com/mens-college-basketball/standings')
    soup = BeautifulSoup(r.content, 'html.parser')
    teams = soup.find_all('td',{'align':'left'})
    for team in teams:
        try:
            url = team.find('a').get('href')
            wrap(url) # add book
        except AttributeError:
            x = 1
        

if __name__ == '__main__':
    main()
