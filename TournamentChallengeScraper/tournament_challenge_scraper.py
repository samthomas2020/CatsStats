from selenium import webdriver
from bs4 import BeautifulSoup
import datetime
import time
import sys
"""
Author: Sam Thomas
Copyright 2018 (c)
License: BSD 2-clause

This is a scraping program that creates a database that generates a CSV with
the Tournament Challenge Picks from a specified ESPN bracket group.
"""

def get_pages(pages, num_urls):
    for page in pages:
        if int(page.get_attribute('data-start')) == num_urls:
            return page

    return None

def get_sites(num_urls):
    new_users = []
    
    # launch browser
    while True:
        browser = webdriver.Firefox()
        try:
            time.sleep(1)
            browser.get('http://games.espn.com/tournament-challenge-bracket/2018/en/group?groupID=1041234')
            time.sleep(1)
            break
        except Exception:
            browser.close()
            time.sleep(2)

    # move browser to search from correct location
    if num_urls > 0:
        page = None
        while True:
            selenium_pages = browser.find_elements_by_class_name('navigationLink')
            while len(selenium_pages) == 0:
                selenium_pages = browser.find_elements_by_class_name('navigationLink')

            page = get_pages(selenium_pages[:-1], num_urls)
            if page is None:
                selenium_pages[-2].click()
                time.sleep(1)
                continue
            else:
                page.click()
                time.sleep(3)
                break

    # initialize the search for the provided duration, if none provided search indefinitely
    
    try:
        duration = int(sys.argv[-1])
    except ValueError:
        duration = int(sys.maxint)

    current_time = datetime.datetime.now()
    delta = datetime.datetime.now() - current_time

    try:
        while delta.seconds < duration:
            new_users.extend([element.get_attribute('href') for element in browser.find_elements_by_class_name('entry')])

            try:
                elements = browser.find_elements_by_class_name('navigationLink')
                elements[-1].click()
            except Exception:
                break

            delta = datetime.datetime.now() - current_time
            continue
    
    except KeyboardInterrupt:
        browser.close()
        f = open('urls.txt', 'a')
        f.write('\n'.join(new_users) + '\n')
        f.close()
        sys.exit()

    browser.close()

    f = open('urls.txt', 'a')
    f.write('\n'.join(new_users) + '\n')
    f.close()

    return new_users

def get_picks(num_picks):
    picks = []

    try:
        f = open('urls.txt', 'r')
        urls = [line.strip() for line in f.readlines()]
        f.close()
    except IOError:
        print "Could not find urls.txt"
        sys.exit()
    
    if num_picks > 0:
        urls = urls[num_picks - 1:]
    
    for bracket in urls:
        user_id = bracket.strip().split('=')[-1]

        # launch site from users bracket
        while True:
            browser = webdriver.Firefox()
            try:
                time.sleep(1)
                browser.get(bracket.strip())
                time.sleep(1)
                break
            except Exception:
                browser.close()
                time.sleep(2)

        html = browser.execute_script('return document.body.innerHTML')
        soup = BeautifulSoup(html, 'html.parser')

        browser.close()

        rank = int(soup.find('span',{'class':'value pct showPCT'}).contents[0])

        # parse out game objects
        games = []
        divs = soup.find_all('div')
        for div in divs:
            c = div.get('class')
            if c is not None and 'matchup m_' in ' '.join(c):
                games.append(div)
        
        # parse out picks from game objects
        user_picks = [user_id, str(rank)]
        for game in games:
            teams = game.find('div',{'class':'slots'}).find_all('div')
            
            team1_seed = teams[0].find_all('span')[1].contents[0]
            team1_name = teams[0].find_all('span')[3].contents[0]
            team1_selected = str('selectedToAdvance' in teams[0].find_all('span')[0].get('class'))
            team1_win = None
            for span in teams[0].find_all('span'):
                c = span.get('class')
                if c is not None and 'actual' in c:
                    if 'winner' in c:
                        team1_win = 'True'
                    else:
                        team1_win = 'False'
                    break

            team2_seed = teams[1].find_all('span')[1].contents[0]
            team2_name = teams[1].find_all('span')[3].contents[0]
            team2_selected = str('selectedToAdvance' in teams[1].find_all('span')[0].get('class'))
            team2_win = None
            for span in teams[1].find_all('span'):
                c = span.get('class')
                if c is not None and 'actual' in c:
                    if 'winner' in c:
                        team2_win = 'True'
                    else:
                        team2_win = 'False'
                    break 

            user_picks.extend([team1_seed, team1_name, team1_selected, team1_win, team2_seed, team2_name, team2_selected, team2_win])
        
        picks.append(user_picks)
        
        try:
            f = open('tournament.csv', 'a')
            f.write(','.join(user_picks) + '\n')
            f.close()
        except IOError:
            print 'Could not open tournament.csv'
            sys.exit()

    return picks




def wrap():
    try:
        f = open('urls.txt', 'r')
        urls = [line.strip() for line in f.readlines()]
        f.close()
    except IOError:
        urls = []
    
    get_sites(len(urls))

    try:
        f = open('tournament.csv', 'r')
        picks = [line.strip() for line in f.readlines()]
        f.close()
    except IOError:
        picks = []

    get_picks(len(picks))

def main():
    wrap()

if __name__ == '__main__':
    main()
