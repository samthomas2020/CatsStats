import scraping_utils
import datetime
import pandas as pd
from time import strptime
"""
Authors: Sam Thomas
Copyright 2018 (c)
License: BSD 2-clause

This is a scraping project developed by the CatsStats student group under the
direction of Dr. Tim Chartier for the use of the USOC to scrape web data for
analysis and ranking of US and world athletes as part of their larger database.
"""

######################################################
## The code below was developed by Sam Thomas and   ##
## it scrapes http://worldcurl.com for individual   ##
## match results as well as team information for    ##
## the USOC's database on curling results. It can   ##
## search back as many years necessary (user-input) ##
## and produces multiple csv files.                 ##
## (1) curling_results.csv: a file that contains    ##
## all of the necessary information to match the    ##
## the USOC's database on individual match results  ##
## (2) curling_teams.csv: a file that stores the    ##
## athletes on each team in the requested format    ##
## from the USOC for their database.                ##
## (3) curling_tournaments.csv: a file that stores  ##
## the final team results of each of the requested  ##
## competitions by the USOC formatted to fit their  ##
## database.                                        ##
######################################################

class Team:
    def __init__(self):
        self.roster = []
        self.skip = None

        self.country = None

        self.place = 9

def acceptable(match):
    if "GSOC" in match and "Tier 1" in match:
        return True
    elif "Masters of Curling" in match:
        return True
    elif "Boost" in match:
        return True
    elif "Meridian" in match:
        return True
    elif "Princess" in match:
        return True
    elif "Players' Championship" in match:
        return True
    elif "Humpty" in match:
        return True
    else:
        return False

def get_teams(soup):
    div = soup.find('div',{'class':'post-container padding'}).find_all('table')
    teams = [Team() for i in range(len(div))]

    for i in range(len(div)):
        team = div[i]
        players = team.find_all('td',{'valign':'top'})[1:-1]

        for player in players:
            name_list = player.find('a',{'class':'wctlight_player_text'}).contents
            name = name_list[0] + ' ' + name_list[-1]
            teams[i].roster.append(name)

            if player.find('font',{'class':'wctlight_player_title'}).contents[0] == "Skip":
                teams[i].skip = name

    return teams

def get_playoffs(soup, teams):
    playoff_teams = []
    for team in soup.find_all('a',{'class':'teams'}):
        try:
            playoff_teams.append(team.contents[0].split(' ')[1])
        except IndexError:
            pass

    if len(playoff_teams) == 11:
        # matchup 1
        if playoff_teams[1] != playoff_teams[3]:
            teams[playoff_teams[1]].place = 5
        else:
            teams[playoff_teams[4]].place = 5

        #matchup 2
        if playoff_teams[7] != playoff_teams[9]:
            teams[playoff_teams[7]].place = 5
        else:
            teams[playoff_teams[10]].place = 5

        #matchup 3
        if playoff_teams[0] != playoff_teams[2]:
            teams[playoff_teams[0]].place = 3
        else:
            teams[playoff_teams[3]].place = 3

        #matchup 4
        if playoff_teams[6] != playoff_teams[8]:
            teams[playoff_teams[6]].place = 3
        else:
            teams[playoff_teams[9]].place = 3

        #matchup 5
        if playoff_teams[2] != playoff_teams[5]:
            teams[playoff_teams[2]].place = 2
            teams[playoff_teams[8]].place = 1
        else:
            teams[playoff_teams[8]].place = 2
            teams[playoff_teams[2]].place = 1

        for team in teams.keys():
            if teams[team].place == 9:
                teams[team].place = 7

    elif len(playoff_teams) == 15:
        # matchup 1
        if playoff_teams[0] != playoff_teams[1]:
            teams[playoff_teams[0]].place = 5
        else:
            teams[playoff_teams[2]].place = 5

        # matchup 2
        if playoff_teams[4] != playoff_teams[5]:
            teams[playoff_teams[4]].place = 5
        else:
            teams[playoff_teams[6]].place = 5

        # matchup 3
        if playoff_teams[8] != playoff_teams[9]:
            teams[playoff_teams[8]].place = 5
        else:
            teams[playoff_teams[9]].place = 5

        # matchup 4
        if playoff_teams[12] != playoff_teams[13]:
            teams[playoff_teams[12]].place = 5
        else:
            teams[playoff_teams[14]].place = 5

        # matchup 5
        if playoff_teams[1] != playoff_teams[3]:
            teams[playoff_teams[1]].place = 3
        else:
            teams[playoff_teams[5]].place = 3

        # matchup 6
        if playoff_teams[9] != playoff_teams[11]:
            teams[playoff_teams[9]].place = 3
        else:
            teams[playoff_teams[13]].place = 3

        # matchup 7
        if playoff_teams[3] != playoff_teams[7]:
            teams[playoff_teams[3]].place = 2
            teams[playoff_teams[11]].place = 1
        else:
            teams[playoff_teams[11]].place = 2
            teams[playoff_teams[3]].place = 1

    return

def parse_event(soup, year, event, gender = "Men"):
    results = []
    teams = {}
    teams_list = []
    tournament = []

    po_fail = False

    teams_value = None
    for item in soup.find('div',{'id':"sub-menu-ul-container"}).find_all('li'):
        try:
            if "Teams" in item.find('a').contents[0]:
                teams_value = item.find('a').get('href')
        except AttributeError:
            pass
    teams_page = scraping_utils.get_site_requests('http://worldcurl.com/' + teams_value)
    for team in get_teams(teams_page):
        teams[team.skip.split(' ')[1]] = team

    scores_value = soup.find('div',{'id':"sub-menu-ul-container"}).find_all('li')[-2].find('a').get('href')
    scores = scraping_utils.get_site_requests('http://worldcurl.com/' + scores_value)

    id = scores_value.split('=')[-1]
    url = 'http://worldcurl.com/events.php?eventid=' + id + '&view=Scores&showdrawid='

    for round in [url + option.get('value') for option in scores.find_all('option')]:
        round_results = parse_draw(scraping_utils.get_site_requests(round), gender, year, teams)
        results.extend(round_results)

    if gender == "Men":
        try:
            href = soup.find('td',{'class':'ysptblclbg7'}).find('a').get('href')
            r, teams_list, tournament = parse_event(scraping_utils.get_site_requests('http://worldcurl.com/' + href), year, event, "Women")
            results.extend(r)
        except AttributeError:
            pass

    playoffs_value = soup.find('div',{'id':"sub-menu-ul-container"}).find_all('li')[-3].find('a').get('href')
    playoffs = scraping_utils.get_site_requests('http://worldcurl.com/' + playoffs_value)

    try:
        get_playoffs(playoffs, teams)
    except KeyError:
        po_fail = True

    for team in teams.keys():
        for member in teams[team].roster:
            x = member.split(' ')[1]
            if team == x:
                l = [teams[team].skip, member + " (Skip)", event, teams[team].country, year]
            else:
                l = [teams[team].skip, member, event, teams[team].country, year]

            if None not in l:
                teams_list.append(l)

        if not po_fail:
            t = ["Curling", "Team", event, gender, teams[team].skip, teams[team].country, teams[team].place]
            tournament.append(t)

    return results, teams_list, tournament

def get_country(c):
    if c == "ON" or c == "MB" or c == "NS" or c == "SK" or c == "NL" or c == "NONT" or c == "AB" or c == "BC":
        return "CAN"
    else:
        return c

def parse_draw(soup, gender, year, teams):
    lines = []

    matches = soup.find_all('table',{'class':'linescorebox'})
    event = soup.find('div',{'class':'post-container page-title'}).contents[0].strip().split(' >')[0]
    font = soup.find('font',{'class':'linescoredrawhead'})

    try:
        date = font.contents[6].split(' --')[0].split(', ')[1]

        month = strptime(date.split(' ')[0], "%b").tm_mon
        if month < 7:
            year += 1
        day = date.split(' ')[1]

        date = str(month) + "/" + day + "/" + str(year)[2:]
    except IndexError:
        try:
            date = font.contents[4].split(' --')[0].split(', ')[1]

            month = strptime(date.split(' ')[0], "%b").tm_mon
            if month < 7:
                year += 1
            day = date.split(' ')[1]

            date = str(month) + "/" + day + "/" + str(year)[2:]
        except IndexError:
            date = "FIND DATE"

    if date == "FIND DATE" or int(year) > datetime.date.today().year:
        return lines
    elif int(year) == datetime.date.today().year and int(month) > datetime.date.today().month:
        return lines
    elif int(year) == datetime.date.today().year and int(month) == datetime.date.today().month and int(day) == datetime.date.today().day:
        return lines

    for match in matches:
        team1 = match.find_all('a',{'class':'linescoreteamlink'})[0].contents[0]
        team2 = match.find_all('a',{'class':'linescoreteamlink'})[1].contents[0]

        country1 = get_country(match.find_all('td',{'class':'linescoreteam'})[0].contents[2].strip().split(', ')[1])
        country2 = get_country(match.find_all('td',{'class':'linescoreteam'})[1].contents[2].strip().split(', ')[1])

        try:
            if teams[team1.split(' ')[1]].country is None:
                teams[team1.split(' ')[1]].country = country1
            if teams[team2.split(' ')[1]].country is None:
                teams[team2.split(' ')[1]].country = country2
        except KeyError:
            pass

        try:
            score1 = match.find_all('td',{'class':'linescorefinal'})[0].contents[1].contents[0]
            score2 = match.find_all('td',{'class':'linescorefinal'})[1].contents[1].contents[0]
        except IndexError:
            score1 = sum([1 if round.find('img') is not None else 0 for round in match.find_all('tr')[1].find_all('td',{'class':'linescoreend'})])
            score2 = sum([1 if round.find('img') is not None else 0 for round in match.find_all('tr')[2].find_all('td',{'class':'linescoreend'})])

        if int(score1) > int(score2):
            result1 = 'WON'
            result2 = 'LOST'
        else:
            result1 = 'LOST'
            result2 = 'WON'

        lines.append([event, 'Curling', 'Team', gender, date, team1, country1, result1, score1, team2, country2, result2, score2])

    return lines

def get_curling(stop_year):
    results = []
    teams = []
    tournaments = []

    soup = scraping_utils.get_site_requests('http://worldcurl.com/schedule.php?et=21#')
    year = int(soup.find('div',{'class':'post-container page-title'}).contents[0].split('-')[0])

    while year != stop_year - 1:
        events = soup.find_all('a',{'class':'scheduleevent'})

        for event in events:
            if acceptable(event.contents[0]):
                r, t, tour = parse_event(scraping_utils.get_site_requests('http://worldcurl.com/' + event.get('href')), year, event.contents[0])

                results.extend(r)
                teams.extend(t)
                tournaments.extend(tour)

        soup = scraping_utils.get_site_requests('http://worldcurl.com/schedule.php?et=21&eventyear=' + str(year))
        year -= 1

    headers = ["Competition Name", "Sport Name", "Event (Weight Category)", "Gender", "Match Date", "Athlete 1 Name", "Athlete 1 Country", "Result 1", "Result Value 1", "Athlete 2 Name", "Athlete 2 Country", "Result 2", "Result Value 2"]

    df1 = pd.DataFrame(results, columns=headers)
    df1.to_csv(path_or_buf="curling_results.csv", index=False)

    df2 = pd.DataFrame(teams, columns=["Team", "Team Member", "Competition", "Country", "Year"])
    df2.to_csv(path_or_buf="curling_teams.csv", index=False)

    df3 = pd.DataFrame(tournaments, columns=["Sport", "Event", "Competition", "Gender", "Athlete", "Country", "Place Finish"])
    df3.to_csv(path_or_buf="curling_tournaments.csv", index=False)

    return 0

def main():
    get_curling(2017)

if __name__ == "__main__":
    main()
