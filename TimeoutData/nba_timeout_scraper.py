import requests
from bs4 import BeautifulSoup
from datetime import timedelta, date
import time

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

start_date = date(2018, 9, 28)
end_date = date.today()

# Get all game urls to scrape from
urls = []
format = 'https://www.espn.com/nba/playbyplay?gameId='

for single_date in daterange(start_date, end_date):
    d = single_date.strftime("%Y%m%d")
    print(d)
    r = requests.get('https://www.espn.com/nba/schedule/_/date/' + d)
    soup = BeautifulSoup(r.content, 'html.parser')

    x = [(d, format + a.get('href').split('=')[1]) for a in soup.find_all('a') if 'gameId' in a.get('href')]

    urls.extend(x)

f = open('timeout_data.csv', 'w')
f.write('Date,AwayTeam,HomeTeam,Quarter,Time,AwayScore,HomeScore,TimeoutTeam,ScoreChange,NextPlay\n')
# Get the play by play data
total = len(urls)
plays = []
for (date, url) in urls:
    if urls.index((date, url)) % 100 == 0:
        print('Reached: ' + str(urls.index((date,url))) + ' out of ' + str(total))

    retries = 0
    while retries < 5:
        try:
            r = requests.get(url)
            break
        except requests.exceptions.ChunkedEncodingError:
            retries += 1
            time.sleep(3)
            continue

    if retries == 5:
        print("Failed to retrieve " + url)
        continue

    soup = BeautifulSoup(r.content, 'html.parser')

    try:
        away, home = [x.text for x in soup.find_all('span',{'class':'abbrev'})]
    except ValueError:
        continue

    quarters = soup.find("div",{"id":"gamepackage-qtrs-wrap"}).find_all("table")

    for q in range(len(quarters)):
        trs = quarters[q].find_all("tr")

        i = 0
        while i < len(trs):
            tr = trs[i]

            if "timeout" in tr.text.lower():
                time = tr.find("td",{"class":"time-stamp"}).text
                score = tr.find("td",{"class":"combined-score"}).text
                timeout_team = tr.find("td",{"class":"game-details"}).text.split(' ')[0]

                # find the next play (after substitutes)
                no_next_play = False
                while True:
                    i += 1
                    try:
                        tr = trs[i]
                    except IndexError:
                        no_next_play = True
                        break

                    if " enters the game for " in tr.text:
                        continue
                    else:
                        break

                if not no_next_play:
                    next_play = tr.find("td", {"class":"game-details"}).text
                    next_score = tr.find("td",{"class":"combined-score"}).text

                    if score.split(' - ')[0] != next_score.split(' - ')[0]:
                        score_change = int(next_score.split(' - ')[0]) - int(score.split(' - ')[0])
                    elif score.split(' - ')[1] != next_score.split(' - ')[1]:
                        score_change = int(next_score.split(' - ')[1]) - int(score.split(' - ')[1])
                    else:
                        score_change = 0
                else:
                    next_play = ""

                plays.append([date, away, home, str(q+1), time, score.split(' - ')[0], score.split(' - ')[1], timeout_team, str(score_change), next_play])

                # convert data to csv
                f.write(','.join(plays[-1]) + '\n')
            else:
                i += 1

f.close()
