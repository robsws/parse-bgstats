import json
import argparse

args_def = argparse.ArgumentParser(description='Parse backup files from BGStats app.')
args_def.add_argument('file', type=argparse.FileType('r'), help='File from which to pull the JSON data.')
args_def.add_argument('--location', '-l', help='Include only games played in this location.')
args_def.add_argument('--start-date', '-s', help='Include only games played after this date.')
args_def.add_argument('--end-date', '-e', help='Include only games played before this date.')
args_def.add_argument('--game', '-g', help='Include only plays of this game.')
args_def.add_argument('--leaderboard-mode', '-m', choices=['wins','medals','points'], help='How the positions on the leaderboard should be decided.')
args = args_def.parse_args()

json_data = args.file.readlines()[0]
bgstats = json.loads(json_data)

def lookup(type, item, id):
    return [x for x in bgstats[type+'s'] if x['id'] == id][0][item]

# Filter stats based on filters passed in
filtered_plays = []
for play in bgstats['plays']:
    if args.location != None and lookup('location', 'name', play['locationRefId']) != args.location:
        continue
    if args.game != None and lookup('game', 'name', play['locationRefId']) != args.game:
        continue
    # TODO: check dates
    filtered_plays.append(play)

#TODO: Calculate the leaderboard

outfile = open('out.txt', 'w')
outfile.write(json.dumps(filtered_plays, indent=2))
# outfile.write(json.dumps(bgstats, indent=2))
