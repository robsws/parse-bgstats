import json
import sys
import argparse

args_def = argparse.ArgumentParser(description='Parse backup files from BGStats app.')
args_def.add_argument('filename', type=argparse.FileType('r'), help='File from which to pull the JSON data.')
args = args_def.parse_args()

print(args)

