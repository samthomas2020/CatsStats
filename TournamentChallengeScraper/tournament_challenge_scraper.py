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
    current = pages[len(pages)/2]
    data_start = int(current.get_attribute('data-start'))

    if len(pages) == 0:
        return None
    if num_urls == data_start:
        return current

    if data_start > num_urls:
        return get_pages(pages[:len(pages)/2], num_urls)
    else:
        return get_pages(pages[len(pages)/2:], num_urls)

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

            page = get_pages(selenium_pages, num_urls)
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

def wrap():
    try:
        f = open('urls.txt', 'r')
        urls = [line.strip() for line in f.readlines()]
        f.close()
    except IOError:
        urls = []
    
    get_sites(len(urls))

    try:
        f = open('picks.txt', 'r')
        picks = [line.strip() for line in f.readlines()]
        f.close()
    except IOError:
        picks = []

    get_picks(len(picks))

def main():
    wrap()

if __name__ == '__main__':
    main()
