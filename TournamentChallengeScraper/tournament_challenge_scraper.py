from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time
import csv
import os

"""
Author: Sam Thomas
Copyright 2018 (c)
License: BSD 2-clause

This is a scraping program that creates a database that generates a CSV with
the Tournament Challenge Picks from a specified ESPN bracket group.
"""

def get_site(url):
    browser = webdriver.Firefox()
    browser.get(url)
    time.sleep(4)
    html = browser.execute_script('return document.body.innerHTML')
    browser.close()
    return BeautifulSoup(html, 'html.parser')

def get_users(url):
    browser = webdriver.Firefox()
    browser.get(url)
    time.sleep(4)

    users = []

    count = 0
    while True:
        html = browser.execute_script('return document.body.innerHTML')
        soup = BeautifulSoup(html, 'html.parser')
        users.extend(soup.find_all('td', {'class':'entryowner wProfile'}))

        next = browser.find_elements_by_class_name('navigationLink')[-1]

        class_name = next.get_attribute('class')
        if 'disabled' not in class_name:
            next.click()
        else:
            print count
            break

        time.sleep(2)

        count += 1

    browser.close()

    return users

def get_data(users):

    print len(users)
    data = [get_picks(user.find('a').get('href')) for user in users[::1000]]
    return data

def get_picks(href):
    soup = get_site('http://games.espn.com/tournament-challenge-bracket/2018/en/' + href)
    slots = soup.find_all('div', {'class':'slots'})

    df = pd.DataFrame(columns=['gameID', 'won'])

    for i in range(len(slots)):
        slotID = int(slots[i].find('div').get('data-slotindex'))/2

        if slots[i].find('span', {'class':'picked eliminated incorrect'}) is not None or slots[i].find('span', {'class':'picked eliminated incorrect selectedToAdvance incorrect'}) is not None:
            row = [slotID, 0]
        else:
            row = [slotID, 1]

        df.loc[i] = row

    return df

def generate_csv(user_data):
    f = open('tournament.csv', 'w')

    writer = csv.writer(f)
    writer.writerow(['pct'] + range(63))

    for i in range(len(user_data)):
        writer.writerow([int(float(i)/len(user_data) * 100)] + user_data[i]['won'].tolist())

    f.close()

def main():
    users = get_users('http://games.espn.com/tournament-challenge-bracket/2018/en/group?groupID=1041234')
    user_data = get_data(users)
    generate_csv(user_data)

if __name__ == '__main__':
    main()
