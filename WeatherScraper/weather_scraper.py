import requests
import urllib3
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
zip_codes = {
    '07073':'EastRutherford','54304':'GreenBay','60605':'Chicago','02035':'Foxboro',
    '48226':'Detroit','64129':'KansasCity','15212':'Pittsburgh','30313':'Atlanta',
    '46225':'Indianapolis','76011':'Dallas','14217':'Buffalo','45202':'Cincinnati',
    '94124':'SanFrancisco','85305':'Phoenix','63101':'StLouis','70112':'NewOrleans',
    '28202':'Charlotte','44114':'Cleveland','98134':'Seattle','55415':'Minneapolis',
    '19148':'Philadelphia','33607':'Tampa','77054':'Houston','33056':'Miami','92108':'SanDiego',
    '32202':'Jacksonville','37213':'Nashville','21230':'Baltimore','80204':'Denver',
    '94621':'Oakland','20785':'WashingtonDC','96818':'Halawa','44708':'Canton','02215':'Boston',
    '10451':'Bronx','11368':'Queens','92806':'Anaheim','76011':'Arlington','53214':'Milwaukee',
    '28036':'Davidson','45469':'Dayton','15282':'Duquesne','22030':'Fairfax','01003':'Amherst',
    '02881':'Kingston','23173':'Richmond','14778':'StBonaventure'
}
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

def get_weather0(code):
    r = requests.get('https://weather.com/weather/tenday/l/'+ code + ':4:US')
    return BeautifulSoup(r.content, 'html.parser')

def get_weather1(code):
    global zip_codes
    html = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    r = html.request('POST', 'https://weather.com/weather/tenday/l/'+ code + ':4:US', headers=agent)
    return BeautifulSoup(r.data, 'html.parser')

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


def update_csv(days, city):
    global zip_codes
    fields = []

    fields.append(datetime.datetime.now())

    for day in days[:10]:
        j = json.loads(day)
        fields.append(j["day"]["temperature"])
        fields.append(j["day"]["precipPct"])

    with open('~/CatsStats/' + city + '_weather_data.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow(fields)

def job():
    global zip_codes
    for code in zip_codes.keys():
        while True:
            soup = get_weather0(code)
            if 'Access Denied' not in soup.find('title').string:
                break

            soup = get_weather1(code)
            if 'Access Denied' not in soup.find('title').string:
                break
            else:
                time.sleep(5)
                continue

        day = get_forecasts(soup)
        update_csv(day, zip_codes[code])

def main():
    # global zip_codes
    # for city in zip_codes.values():
    #     with open(city + '_weather_data.csv', 'w') as f:
    #         writer = csv.writer(f)
    #         writer.writerow(['timestamp', 'day_1_temp', 'day_1_precip', 'day_2_temp', 'day_2_precip', 'day_3_temp', 'day_3_precip', 'day_4_temp', 'day_4_precip', 'day_5_temp', 'day_5_precip', 'day_6_temp', 'day_6_precip', 'day_7_temp', 'day_7_precip', 'day_8_temp', 'day_8_precip', 'day_9_temp', 'day_9_precip', 'day_10_temp', 'day_10_precip'])
    #
    # schedule.every().day.at("00:00").do(job)
    #
    # while True:
    #     schedule.run_pending()
    #     time.sleep(60) # wait one minute

    job()

if __name__ == '__main__':
    main()
