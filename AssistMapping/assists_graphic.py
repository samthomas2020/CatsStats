import requests
from bs4 import BeautifulSoup
import graphics
import math
import xlsxwriter
import csv

"""
This is a program based on an idea by Dr. Tim Chartier and the student group
CatStats at Davidson College. The program scrapes data from ESPN's 
"Play-by-Play" interface and creates a graphical representation of who gave and
received assists in a game.

The information is stored in both a list of relevant assists for each player in
terms of who has received an assist from that player/who they have received
assists from and mapped with a quantity in a dictionary. Additionally, the
information is saved as a 2x2 array of lists for both the home and away teams
called GameData.home_array and GameData.away_array.

Author: Sam Thomas
"""
class Player:
    def __init__(self, name):
        self.name = name
        if ' ' in name and name.index(' ') != len(name) - 1:
            space = name.index(' ')
            self.last_name = name[space + 1:]
        else:
            self.last_name = name
        self.assisted = {}
        self.received = {}
        # arbitrary circle for circular representation of graphic
        self.circle = graphics.Circle(graphics.Point(10,10), 10)
        # arbitrary intersection point for circular representation of graphic
        self.int_point = graphics.Point(10,10)
    
    def add_assist(self, player):
        if player in self.assisted:
            self.assisted[player] += 1
        else:
            self.assisted[player] = 1
    
    def add_received(self, player):
        if player in self.received:
            self.received[player] += 1
        else:
            self.received[player] = 1
            
    def assisted(self):
        return self.assisted
    
    def received(self):
        return self.received

class GameData:
    def __init__(self, url):
        self.url = url
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        plays = soup.find_all("td", {"class": "game-details"})
        images = soup.find_all("img", {"class": "team-logo"})
        self.away_assists = []
        self.home_assists = []
        self.away_players = []
        self.home_players = []
        self.away_array = []
        self.home_array = []
        away_image = images[0].get('src')
        home_image = images[1].get('src')
        
        value = len(images) - len(plays)
        
        if 'nba' in url:
            self.is_college = False  
        else:
            self.is_college = True
        
        for i in range(len(plays)):
            play = plays[i].contents[0]
            if 'Assisted by' in play or 'assists)' in play:
                if images[i + value].get('src') == away_image:
                    self.away_assists.append(play)
                else:
                    self.home_assists.append(play)
        
    def generate_usable_data(self):
        away_player_names = []
        home_player_names = []
        
        for play in self.away_assists:
            # come up with the scorer and passer in all plays for the away team
            if self.is_college == True:
                score = play.split('. Assisted')[0]
                scorer = score.split(' made')[0]
                assist = play.split('. Assisted')[1]
                passer = assist.split('by ')[1][:-1]
            else:
                score = play.split('(')[0]
                scorer = score.split(' makes')[0]
                assist = play.split('(')[1]
                passer =  assist.split(' assists')[0]
            
            # generate the Player objects for the players and store them in the
            # appropriate lists
            if scorer not in away_player_names:
                scoring_player = Player(scorer)
                away_player_names.append(scorer)
                self.away_players.append(scoring_player)
            else:
                index = away_player_names.index(scorer)
                scoring_player = self.away_players[index]
            
            if passer not in away_player_names:
                passing_player = Player(passer)
                away_player_names.append(passer)
                self.away_players.append(passing_player)
            else:
                index = away_player_names.index(passer)
                passing_player = self.away_players[index]
            
            # add each player to the other players lists and update the
            # frequency of that occurence
            passing_player.add_assist(scoring_player)
            scoring_player.add_received(passing_player)
    
        
        for play in self.home_assists:
            # come up with the scorer and passer in all plays for the away team
            if self.is_college == True:
                score = play.split('. Assisted')[0]
                scorer = score.split(' made')[0]
                assist = play.split('. Assisted')[1]
                passer = assist.split('by ')[1][:-1]
            else:
                score = play.split('(')[0]
                scorer = score.split(' makes')[0]
                assist = play.split('(')[1]
                passer =  assist.split(' assists')[0]
            
            # generate the Player objects for the players and store them in the
            # appropriate lists
            if scorer not in home_player_names:
                scoring_player = Player(scorer)
                home_player_names.append(scorer)
                self.home_players.append(scoring_player)
            else:
                index = home_player_names.index(scorer)
                scoring_player = self.home_players[index]
            
            if passer not in home_player_names:
                passing_player = Player(passer)
                home_player_names.append(passer)
                self.home_players.append(passing_player)
            else:
                index = home_player_names.index(passer)
                passing_player = self.home_players[index]
            
            # add each player to the other players lists and update the
            # frequency of that occurence
            passing_player.add_assist(scoring_player)
            scoring_player.add_received(passing_player) 
            
        # make the away_array
        for player in away_player_names:
            self.away_array.append([])
        
        for i in range(len(self.away_players)):
            for j in range(len(self.away_players)):
                if self.away_players[j] in self.away_players[i].assisted:
                    self.away_array[i].append(self.away_players[i].assisted[self.away_players[j]])
                else:
                    self.away_array[i].append(0)
        
        # make the home_array
        for player in home_player_names:
            self.home_array.append([])
        
        for i in range(len(self.home_players)):
            for j in range(len(self.home_players)):
                if self.home_players[j] in self.home_players[i].assisted:
                    self.home_array[i].append(self.home_players[i].assisted[self.home_players[j]])
                else:
                    self.home_array[i].append(0)        
    
    def create_circle_graphic(self):
        # set away and home windows
        away_win = graphics.GraphWin('Assist Chart -- Away', 500, 500)
        home_win = graphics.GraphWin('Assist Chart -- Home', 500, 500)
        away_win.setBackground('black')
        home_win.setBackground('red')
        
        BIG_RADIUS = 200
        SMALL_RADIUS = 25
        
        # set circles, int_points, and write last names for each away_player
        for i in range(1, len(self.away_players) + 1):
            angle = (2 * math.pi * i)/len(self.away_players)
            
            x = (BIG_RADIUS * math.cos(angle)) + 250
            y = (BIG_RADIUS * math.sin(angle)) + 250
            mini_circle = graphics.Circle(graphics.Point(x,y), SMALL_RADIUS)
            mini_circle.setFill('red')
            self.away_players[i - 1].circle = mini_circle
            
            int_x = (SMALL_RADIUS * math.cos(angle + math.pi)) + x
            int_y = (SMALL_RADIUS * math.sin(angle + math.pi)) + y
            self.away_players[i - 1].int_point = graphics.Point(int_x,int_y)
            
            text = graphics.Text(graphics.Point(x,y), self.away_players[i - 1].last_name)
            text.setSize(8)
            text.setFill('white')
            
            mini_circle.draw(away_win)
            text.draw(away_win)
        
        for player in self.away_players:
            for assist in player.assisted:
                line = graphics.Line(player.int_point, assist.int_point)
                line.setFill('white')
                line.setWidth(player.assisted[assist] * 2)
                line.setArrow('last')
                line.draw(away_win)
        
        # do the same for the home team
        for i in range(1, len(self.home_players) + 1):
            angle = (2 * math.pi * i)/len(self.home_players)
            
            x = (BIG_RADIUS * math.cos(angle)) + 250
            y = (BIG_RADIUS * math.sin(angle)) + 250
            mini_circle = graphics.Circle(graphics.Point(x,y), SMALL_RADIUS)
            mini_circle.setFill('black')
            self.home_players[i - 1].circle = mini_circle
            
            int_x = (SMALL_RADIUS * math.cos(angle + math.pi)) + x
            int_y = (SMALL_RADIUS * math.sin(angle + math.pi)) + y
            self.home_players[i - 1].int_point = graphics.Point(int_x,int_y)
            
            text = graphics.Text(graphics.Point(x,y), self.home_players[i - 1].last_name)
            text.setSize(8)
            text.setFill('white')
            
            mini_circle.draw(home_win)
            text.draw(home_win)
        
        for player in self.home_players:
            for assist in player.assisted:
                line = graphics.Line(player.int_point, assist.int_point)
                line.setFill('white')
                line.setWidth(player.assisted[assist] * 2)
                line.setArrow('last')
                line.draw(home_win)
                
        away_win.getMouse()
        away_win.close()
        home_win.getMouse()
        home_win.close()
    
    def export_data(self):
        filename = "gamedata" + self.url.split('=')[1]
        book = xlsxwriter.Workbook(filename+".xlsx")
        away_sheet = book.add_worksheet("Away")
        home_sheet = book.add_worksheet("Home")
        
        # input data in away_sheet
        for i in range(1, len(self.away_array) + 1):
            away_sheet.write_string(i, 0, self.away_players[i - 1].last_name)
            away_sheet.write_string(0, i, self.away_players[i - 1].last_name)
        
        for row in range(1, len(self.away_array) + 1):
            for col in range(1, len(self.away_array[row - 1]) + 1):
                away_sheet.write_number(row, col, self.away_array[row - 1][col - 1])
        
        # input data in home_sheet
        for i in range(1, len(self.home_array) + 1):
            home_sheet.write_string(i, 0, self.home_players[i - 1].last_name)
            home_sheet.write_string(0, i, self.home_players[i - 1].last_name)
        
        for row in range(1, len(self.home_array) + 1):
            for col in range(1, len(self.home_array[row - 1]) + 1):
                home_sheet.write_number(row, col, self.home_array[row - 1][col - 1])
        
        # save the sheet
        book.close()
    
    def export_csv_files(self):
        filename = "gamedata-away.csv"
        with open(filename, 'w') as out_file:
            wr = csv.writer(out_file, quoting=csv.QUOTE_NONNUMERIC)
            wr.writerow(['assister','receiver','number'])
            for assister in self.away_players:
                for receiver in assister.assisted:
                    to_write = ['']
                    for player in away_players:
                        to_write.append(player.name)
                    wr.writerow([assister.last_name, receiver.last_name, assister.assisted[receiver]])
        
        filename = "gamedata-home.csv"
        with open(filename, 'w') as out_file:
            wr = csv.writer(out_file, quoting=csv.QUOTE_NONNUMERIC)
            wr.writerow(['assister','receiver','number'])
            for assister in self.home_players:
                for receiver in assister.assisted:
                    wr.writerow([assister.last_name, receiver.last_name, assister.assisted[receiver]])
                    
    def export_better_files(self):
        with open('away_data.csv', 'w') as f:
            wr = csv.writer(f)
            to_write = ['']
            for player in self.away_players:
                to_write.append(player.name)
            wr.writerow(to_write)
            for i in range(len(self.away_players)):
                to_write = [self.away_players[i].name] + self.away_array[i]
                wr.writerow(to_write)
        
    
def main():
    url = raw_input('Paste url here: ')
    g = GameData(url)
    g.generate_usable_data()
    #g.export_data()
    #g.export_csv_files()
    g.export_better_files()
    g.create_circle_graphic()
    
if __name__ == '__main__':
    main()
