import json
import sys
import argparse

args_def = argparse.ArgumentParser(description='Parse backup files from BGStats app.')
args_def.add_argument('file', type=argparse.FileType('r'), help='File from which to pull the JSON data.')
args = args_def.parse_args()

json_data = args.file.readlines()[0]
bgstats = json.loads(json_data)

outfile = open('out.txt', 'w')
outfile.write(json.dumps(bgstats, indent=2))
