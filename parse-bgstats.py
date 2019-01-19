import json
import argparse
from collections import defaultdict
from tabulate import tabulate

args_def = argparse.ArgumentParser(description='Parse backup files from BGStats app.')
args_def.add_argument('file', type=argparse.FileType('r'), help='File from which to pull the JSON data.')
args_def.add_argument('--location', '-l', help='Include only games played in this location.')
args_def.add_argument('--startdate', '-s', help='Include only games played after this date.')
args_def.add_argument('--enddate', '-e', help='Include only games played before this date.')
args_def.add_argument('--game', '-g', help='Include only plays of this game.')
args_def.add_argument('--mode', '-m', default='wins', choices=['wins','medals','points'], help='How the positions on the leaderboard should be decided.')
args = args_def.parse_args()

json_data = args.file.readlines()[0]
bgstats = json.loads(json_data)

def lookup(type, item, id):
    return [x for x in bgstats[type+'s'] if x['id'] == id][0][item]

def scores():
    return {'gold':0,'silver':0,'bronze':0} if args.mode == 'medals' else 0

leaderboard = defaultdict(scores)

for play in bgstats['plays']:
    # Filter stats based on filters passed in
    # TODO: allow filter by multiple locations/games
    if args.location != None and lookup('location', 'name', play['locationRefId']) != args.location:
        continue
    if args.game != None and lookup('game', 'name', play['locationRefId']) != args.game:
        continue
    # TODO: check dates
    # Calculate leaderboard stats for this game
    player_scores = {lookup('player','name',score['playerRefId']):{'winner':1 if score['winner'] else 0,'score':score['score']} for score in play['playerScores']}
    sorted_players = sorted(player_scores.items(), key=lambda kv: int(kv[1]['score']) if kv[1]['score'] != None and kv[1]['score'] != '' else kv[1]['winner'], reverse=True)
    sorted_players = sorted(sorted_players, key=lambda kv: int(kv[1]['winner']), reverse=True)
    if args.mode == 'wins':
        leaderboard[sorted_players[0][0]] += 1
    elif args.mode == 'medals':
        leaderboard[sorted_players[0][0]]['gold'] += 1
        # Only hand out silver and bronze if there were numerical scores
        if sorted_players[1][1]['score'] != None and sorted_players[1][1]['score'] != '':
            leaderboard[sorted_players[1][0]]['silver'] += 1
            leaderboard[sorted_players[2][0]]['bronze'] += 1
    elif args.mode == 'points':
        for score in sorted_players:
            leaderboard[score[0]] += int(score[1]['score']) if score[1]['score'] != None else score[1]['winner']

# Sort the leaderboard
GOLD_POINTS = 5
SILVER_POINTS = 2
BRONZE_POINTS = 1
# TODO: make points for gold, silver, bronze configurable
def melt_medals(medals):
    return medals['gold'] * GOLD_POINTS + medals['silver'] * SILVER_POINTS + medals['bronze'] * BRONZE_POINTS

if args.mode == 'medals':
    sorted_leaderboard = sorted(leaderboard.items(), key=lambda kv: melt_medals(kv[1]), reverse=True)
else:
    sorted_leaderboard = sorted(leaderboard.items(), key=lambda kv: kv[1], reverse=True)

# Print the leaderboard
table_data = [list(t) for t in sorted_leaderboard]
print(tabulate(table_data, headers=['Name', 'Score']))

outfile = open('out.txt', 'w')
outfile.write(json.dumps(bgstats, indent=2))
