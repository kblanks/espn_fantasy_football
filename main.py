import requests
import pandas as pd
import numpy as np

# pd.set_option('display.max_columns', None)

# Needed for accessing private league
cookies = {
  "espn_s2": 'AECMnjlyyYfS8szHcZSE3Xa9mfMaA12A7W5hbsoOPH1poc7CIsf3l5Y6FZRMlPpBa8BTCP4Rb1uztgqwk%2FWKRSEV%2BYQZr2jG0XyjGyz8yZxcne2rc5edV%2FoKD2wW%2BJul9PoxYuEricjtU%2BNn5yx2T32FJ5VuCo0CYMf4bZo0WPU0rSzeAvGlDZ2zaR3J4%2Fny5m4u9OJ1F0E6f97uVurf9XmwKn9uxpdYsa9LSBaYCIA%2BrMGWVLwDA7AozNrZQZTJHDI1nGaR2z3rclHJS6piIYlu25EiAlhDf1ruC%2BY2VRCGohotrgC1dglJQ%2FmDvoR9U7I%3D',
  "SWID": '{3E416C6D-2A8D-4A88-91D4-2F5D31D7C5C2}'
};

# League Definitions
leagueID = 1793518;
year = 2022;

# API SetupS
url = "https://fantasy.espn.com/apis/v3/games/ffl/seasons/" + \
      str(year) + "/segments/0/leagues/" + str(leagueID)

# Manager/User Data
r = requests.get(url, cookies=cookies, params={"view": "mTeam"})
d = r.json()
owners_df = [[
    owner['id'],
    owner['displayName'],
    owner['firstName'],
    owner['lastName']
    ] for owner in d['members']]
owners_df = pd.DataFrame(owners_df, columns=['ID', 'USER_NAME', 'FIRST', 'LAST'])
# print(owners_df)
teams_df = [[
    team['id'],
    team['location'],
    team['nickname'],
    team['primaryOwner']
    ] for team in d['teams']]
teams_df = pd.DataFrame(teams_df, columns=['ID', 'LOC', 'ABBR', 'OWNER_ID'])
# print(teams_df)

# Schedule/Matchup Data
r = requests.get(url, cookies=cookies, params={"view": "mMatchup"})
d = r.json()

currentWeek = d['scoringPeriodId']

schedule_df = [[
    game['matchupPeriodId'],
    game['id'],
    game['winner'],
    game['away']['teamId'],
    game['away']['totalPoints'],
    game['home']['teamId'],
    game['home']['totalPoints'],
    ] for game in d['schedule']]
schedule_df = pd.DataFrame(schedule_df, columns=['WEEK', 'ID', 'WINNER', 'AWAY_TEAM_ID', 'AWAY_TEAM_SCORE', 'HOME_TEAM_ID', 'HOME_TEAM_SCORE'])
schedule_df['Type'] = ['Regular' if w <= 15 else 'Playoff' for w in schedule_df['WEEK']]
schedule_df['WINNING_SCORE'] = schedule_df[['HOME_TEAM_SCORE', 'AWAY_TEAM_SCORE']].max(axis=1)
schedule_df['LOSING_SCORE'] = schedule_df[['HOME_TEAM_SCORE', 'AWAY_TEAM_SCORE']].min(axis=1)
print(schedule_df)

# Figure out High/Low Scorers
# schedule_df.sort_values()

highScore = 0
lowScore = 999999
newWinner = False
newLoser = False

for index, row in schedule_df.iterrows():
    if row['WINNER'] == 'UNDECIDED':
        break
    if row['AWAY_TEAM_SCORE'] > highScore:
        highScore = row['AWAY_TEAM_SCORE']
        highWeek = row['WEEK']
        highTeam = row['AWAY_TEAM_ID']
    if row['HOME_TEAM_SCORE'] > highScore:
        highScore = row['HOME_TEAM_SCORE']
        highWeek = row['WEEK']
        highTeam = row['HOME_TEAM_ID']
    if row['AWAY_TEAM_SCORE'] < lowScore:
        lowScore = row['AWAY_TEAM_SCORE']
        lowWeek = row['WEEK']
        lowTeam = row['AWAY_TEAM_ID']
    if row['HOME_TEAM_SCORE'] < lowScore:
        lowScore = row['HOME_TEAM_SCORE']
        lowWeek = row['WEEK']
        lowTeam = row['HOME_TEAM_ID']

# print(highScore, highWeek, highTeam)
# print(teams_df.loc[teams_df['ID'] == highTeam][['LOC', 'ABBR']])
if highWeek == currentWeek:
    newWinner = True
# print(lowScore, lowWeek, lowTeam)
# print(teams_df.loc[teams_df['ID'] == lowTeam][['LOC', 'ABBR']])
if lowWeek == currentWeek:
    newLoser = True
