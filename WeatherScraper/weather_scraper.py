import urllib3
from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.common.exceptions import TimeoutException
import certifi
from bs4 import BeautifulSoup
import json
import csv
import time
import schedule
import datetime

"""
Author: Sam Thomas
Copyright 2018 (c)
License: BSD 2-clause

This is a scraping program that creates a database that generates a CSV with
the weather data from a specified city. It is currently set to Davidson, NC.
"""

agent = {"User-Agent":'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}

def disableImages():
    ## get the Firefox profile object
    firefoxProfile = FirefoxProfile()
    ## Disable CSS
    firefoxProfile.set_preference('permissions.default.stylesheet', 2)
    ## Disable images
    firefoxProfile.set_preference('permissions.default.image', 2)
    ## Disable Flash
    firefoxProfile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so',
                                  'false')
    ## Set the modified profile while creating the browser object
    return firefoxProfile

def get_weather1():
    html = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    r = html.request('POST', 'https://weather.com/weather/tenday/l/28036:4:US', headers=agent)
    return BeautifulSoup(r.data, 'html.parser')

def get_weather2(profile):
    browser = webdriver.Firefox(profile)
    browser.get('https://weather.com/weather/tenday/l/28036:4:US')
    html = browser.execute_script('return document.body.innerHTML')
    browser.close()
    return BeautifulSoup(html, 'html.parser')

def get_current_weather(soup):
    scripts = soup.find_all('script')

    s = ''
    for script in scripts:
        s = script.split('adaptorParams = ')[-1].split(';')[0]
        if s != '':
            break

def get_forecasts(soup):
    scripts = soup.find_all('script')

    s = ''
    data = []
    for script in scripts:
        s = script.string
        if s is not None:
            info = []
            s = s.split('window.__data=')[-1]
            if s != '' and '"pageType":"tenday","reducerKey":"10dayForecast"' in s:
                days = s.split(',{"validDate":')

                for day in days:
                    info.append('{"validDate":' + day)

                for i in info:
                    try:
                        j = json.loads(i)
                        keys = j.keys()
                        data.append(i)
                    except ValueError:
                        pass

                return data


def update_csv(days):
    fields = []

    fields.append(datetime.datetime.now())

    for day in days[:10]:
        j = json.loads(day)
        fields.append(j["day"]["temperature"])
        fields.append(j["day"]["precipPct"])

    with open('davidson_weather_data.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow(fields)

def job():
    while True:
        try:
            print "Trying to pull weather remotely...."
            soup = get_weather1()
            break
        except Exception:
            print "Failed...."
            continue

    if 'Access Denied' in soup.find('title').string:
        profile = disableImages()
        while True:
            try:
                print "Trying to pull weather with Selenium...."
                soup = get_weather2(profile)
                break
            except Exception:
                print "Failed, trying again...."
                continue

    print "Got weather...."
    days = get_forecasts(soup)
    update_csv(days)

def main():
    # with open('davidson_weather_data.csv', 'w') as f:
    #     # writer = csv.writer(f)
    #     # writer.writerow(['timestamp', 'day_1_temp', 'day_1_precip', 'day_2_temp', 'day_2_precip', 'day_3_temp', 'day_3_precip', 'day_4_temp', 'day_4_precip', 'day_5_temp', 'day_5_precip', 'day_6_temp', 'day_6_precip', 'day_7_temp', 'day_7_precip', 'day_8_temp', 'day_8_precip', 'day_9_temp', 'day_9_precip', 'day_10_temp', 'day_10_precip'])

    schedule.every().day.at("00:00").do(job)

    while True:
        schedule.run_pending()
        time.sleep(60) # wait one minute

if __name__ == '__main__':
    main()
