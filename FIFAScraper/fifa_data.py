from selenium import webdriver
from bs4 import BeautifulSoup
import csv
import datetime
"""
This is a program that will scrape data from the FIFA site by month to create a
database in the form of a csv file that contains information. The site is
scraped with a selenium webdiver.
Author: Sam Thomas
"""
VALID = {'Continental_Final':['Continental Final'], 'Continental Qualifier':['Continental Qualifier'],
        'FIFA_Confederations_Cup':['FIFA Confederations Cup'], 'FIFA_World_Cup_Final':['FIFA World Cup Final'],
        'FIFA_World_Cup_Qualifier':['FIFA World Cup Qualifier'], 'Friendly':['Friendlies']}

def get_site(url):
    browser = webdriver.Firefox()
    browser.get(url)
    html = browser.execute_script('return document.body.innerHTML')
    browser.close()
    return BeautifulSoup(html, 'html.parser')

def parse_date(time):
    year = time.split('-')[0]
    month = time.split('-')[1]
    day = time.split('-')[2].split('T')[0]
    return day+'/'+month+'/'+year

def deal_with_pso(pso, winner):
    score = pso.split('(')[1].split(')')[0]
    if score == pso:
        return
    if winner == 'home':
        return [score.split(' - ')[0], score.split(' - ')[1]]
    else:
        return [score.split(' - ')[1], score.split(' - ')[2]]

def get_month(soup):
    sections = soup.find_all('div',{'class':'competition-row'})
    for section in sections:
        valid = False
        for v in VALID:
            if section.find('span',{'class':'comp-t-name'}).contents[0] in VALID[v]:
                print "Working with this month's %s" % v
                games = section.find_all('div',{'class':'ls-mu'})
                for game in games:
                    score = []
                    score.append(game.find('span',{'class':'t-name'}).contents[0].replace(' ', '_'))
                    home_score = game.find('span',{'class':'score-home'}).contents[0]
                    score.append(home_score)
                    away_score = game.find('span',{'class':'score-away'}).contents[0]
                    score.append(away_score)
                    if int(home_score) > int(away_score):
                        winner = 'home'
                    else:
                        winner = 'away'                
                    score.append(game.find_all('span',{'class':'t-name'})[-1].contents[0].replace(' ', '_'))
                    score.append(parse_date(game.get('data-matchdate')))
                    score.append(game.find('span',{'class':'venue'}).contents[0])
                    score.append(v)
                    if (game.find('div',{'class':'ls-mu-rw'}) != None):
                        score.extend(deal_with_pso(game.find('div',{'class':'ls-mu-rw'}).contents[0].contents[0]), winner)
                    with open("FIFA_2006_toApr2018.csv", 'a') as f:
                        writer = csv.writer(f)
                        writer.writerow(score)
                    print "Match added...."
            else:
                pass

def wrap():
    now = datetime.datetime.now()
    print "Getting site....."
    #TODO: iterate over every month
    soup = get_site("http://www.fifa.com/live-scores/international-tournaments/fixtures-results/index.html#month"+str(now.month - 1)+"-"+str(now.year))
    print "Site html received...."
    scores = get_month(soup)
    print "Data received and added....."
        

def main():
    wrap()

if __name__ == '__main__':
    main()
