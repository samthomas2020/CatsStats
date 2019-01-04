import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import time
"""
Author: Sam Thomas
Copyright 2018 (c)
License: BSD 2-clause

These methods are commonly used in webscraping projects for Cats Stats, a
student statistics group at Davidson College in Davidson, NC.
"""

def get_site_requests(url):
    r = requests.get(url)
    return BeautifulSoup(r.content, 'html.parser')

def get_site_selenium(url):
    browser = webdriver.Firefox()
    browser.get(url)
    time.sleep(1)
    html = browser.execute_script('return document.body.innerHTML')
    browser.close()
    return BeautifulSoup(html, 'html.parser')
