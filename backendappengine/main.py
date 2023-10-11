import requests
from flask import Flask
import json;
from json import JSONEncoder;
from datetime import datetime;

def get_week_number(now):
    date = datetime(now.year,now.month,now.day)
    start_date = datetime(2023,9,7)
    return date.isocalendar()[1] - start_date.isocalendar()[1]

class Company:
    def __init__(self,league_list,current_week):
        self.league_list = league_list
        self.current_week = current_week

class CompanyEncoder(JSONEncoder):
    def default(self,o):
        return o.__dict__

class League:
    def __init__(self,name:str,league_id:int, player_list,matchup_list):
        self.name = name
        self.league_id = league_id
        self.player_list = player_list
        self.matchup_list = matchup_list
        
        
class LeagueEncoder(JSONEncoder) :
    def default(self,o):
        return o.__dict__     

class Player:
    def __init__(self, name: str, wins: int, losses: int, ties: int,points: int):
        self.name = name
        self.wins = wins
        self.losses = losses
        self.ties = ties
        self.points = points

class PlayerEncoder(JSONEncoder):
        def default(self, o):
            return o.__dict__
        
class Matchup:
    def __init__(self,home_team:str,away_team: str,home_points:int ,away_points: int):
        self.home_team = home_team
        self.away_team = away_team
        self.home_points = home_points
        self.away_points = away_points 
        

class MatchupEncoder(JSONEncoder):
    def default(self,o):
        return o.__dict__
app = Flask(__name__)

@app.route('/data')
def data():
   
   company_data = Company(None,None)
   
   ##league ID's
   league_id_m = 1716588255
   league_id_l = 520149224
   league_id_w = 258973210

   league_ids = [league_id_l, league_id_m, league_id_w]
   

   #instantiate a Company class
   league_list = []
   company_data = Company(league_list,get_week_number(datetime.today()))

   # fetch scoreboard data
   for i in league_ids:

      url = 'https://fantasy.espn.com/apis/v3/games/ffl/seasons/2023/segments/0/leagues/' + str(i)
      
      #fetch league name and id
      r = requests.get(url).json()
      name = r['settings']['name']
      league_data = League(name,i,None,None)


      ##get team names,where id is key and team name/scores are values
      teamId = {}
      teamRecord = {}
      names = []

      r = requests.get(url, params={"view": "mTeam"}, verify=False).json()
      
      ids = {}
      
      count = 1
      for member in r['members']:
         teamId[count] = member['firstName'].title() + " " + member['lastName'].title() + "."
         names.append(member['firstName'].title() + " " + member['lastName'].title())
         ids[member['id']] = member['firstName'].title() + " " + member['lastName'].title()
         count += 1
      if i != league_id_m:
          names.remove('Kris Gibson')
      
      count = 1
      for team in r['teams']:
         wins = team['record']['overall']['wins']
         losses = team['record']['overall']['losses']
         ties = team['record']['overall']['ties']
         points = team['points']
         for i in ids.keys():
             if team['primaryOwner'] == i:
                  first_name, last_name = ids[i].split()
                  last_initial = last_name[0] + "."
                  result = first_name + " " + last_initial
                  teamRecord[count] = [result, wins, losses, ties,points]
                 
                 
        #  for k in names:
        #     if team['nickname'].title() in k: 
        #         first_name, last_name = k.title().split()
        #         last_initial = last_name[0] + "."
        #         result = first_name + " " + last_initial
        #         teamRecord[count] = [result, wins, losses, ties,points]
                
        #     if team['nickname'] == 'Gibson' and i==league_id_w:
                
        #         result = "Ricci" + " " + "R."
        #         teamRecord[count] = [result, wins, losses, ties,points]
                
        #     if team['nickname'] == "Gibson" and i == league_id_l:
        #         result = "Eric" + " " + "W."
        #         teamRecord[count] = [result, wins, losses, ties,points]
         count += 1

      

      teamlist = []
      for i in teamRecord:
         player = Player(teamRecord[i][0],teamRecord[i][1],teamRecord[i][2],teamRecord[i][3],teamRecord[i][4])
         teamlist.append(player)


      league_data.player_list = teamlist 

      #get matchup data
      r = requests.get(url, params={"view": "mMatchup"}, verify=False).json()
      s = requests.get(url, params={"view": "mTeam"}, verify=False).json()
      matchups = []
      for matchup in r['schedule']:
          week = matchup['matchupPeriodId']
          
          if week == company_data.current_week:
              
              away_team = matchup['away']['teamId']
              away_points = matchup['away']['totalPoints']
              home_team = matchup['home']['teamId']
              home_points = matchup['home']['totalPoints']
              for team in s['teams']:
                  if team['id'] == home_team:
                      for i in ids.keys():
                          if team['primaryOwner'] == i:
                              first_name, last_name = ids[i].split()
                              last_initial = last_name[0] + "."
                              result = first_name + " " + last_initial
                              home_team = result
                  if team['id'] == away_team:
                      for i in ids.keys():
                          if team['primaryOwner'] == i:
                              first_name, last_name = ids[i].split()
                              last_initial = last_name[0] + "."
                              result = first_name + " " + last_initial
                              away_team = result
              
                      
                      

              matchup_info = Matchup(home_team,away_team,home_points,away_points)
              matchups.append(matchup_info)


      league_data.matchup_list = matchups

      company_data.league_list.append(league_data)  


      
      
   
   company_json = json.dumps(company_data,indent=4,cls=CompanyEncoder)    
   
   #ENABLE CORS from any web address
   return company_json,{'Access-Control-Allow-Origin': "*"}


    
    
   
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True)