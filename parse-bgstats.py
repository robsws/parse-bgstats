import json
import argparse
import mysql.connector
import os

args_def = argparse.ArgumentParser(description='Parse backup files from BGStats app and load to SQL.')
args_def.add_argument('file', type=argparse.FileType('r'), help='File from which to pull the JSON data.')
args = args_def.parse_args()

bgstats = json.load(args.file)

sql = mysql.connector.connect(
    user=os.environ('bgstats_sql_user'),
    password=os.environ('bgstats_sql_password'),
    host=os.environ('bgstats_sql_host'),
    database=os.environ('bgstats_sql_database')
)

cursor = sql.cursor()
cursor.execute('DELETE FROM Score')
cursor.execute('DELETE FROM Play')
cursor.execute('DELETE FROM Location')
cursor.execute('DELETE FROM Game')
cursor.execute('DELETE FROM Player')
sql.commit()

for player in bgstats['players']:
    cursor.execute('''
        INSERT INTO Player (player_id, player_name)
        VALUES (%s, %s)
    ''', [player['id'], player['name']])

sql.commit()

for game in bgstats['games']:
    cursor.execute('''
        INSERT INTO Game (game_id, game_name)
        VALUES (%s, %s)
    ''', [game['id'], game['name']])

sql.commit()

for location in bgstats['locations']:
    cursor.execute('''
        INSERT INTO Location (location_id, location_name)
        VALUES (%s, %s)
    ''', [location['id'], location['name']])

sql.commit()

for play in bgstats['plays']:
    cursor.execute('''
        INSERT INTO Play (game_id, location_id, entry_date, play_date)
        VALUES (%s, %s, %s, %s)
    ''', [play['gameRefId'], play['locationRefId'], play['entryDate'], play['playDate']])
    play_id = cursor.lastrowid
    sql.commit()
    for score in play['playerScores']:
        cursor.execute('''
            INSERT INTO Score (play_id, player_id, score, winner, `rank`)
            VALUES (%s, %s, %s, %s, %s)
        ''', [play_id, score['playerRefId'], score['score'] if score['score'] != '' else None, 1 if score['winner'] else 0, score['rank']])

sql.commit()