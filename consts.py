import json
import os

DAILY_DT_FORMAT = r"%m/%d/%Y" #01/01/2023
LOG_DT_FORMAT = r"%Y:%m:%d:"
EMBED_COLOR = 0xe620c1
ACTIVITY_DATA = os.path.abspath('data/activity.json')
CHERRIES_DATA = os.path.abspath('data/cherriesS.json')

CHERRIES_MULTIPLIER = 10

"""
Read json file data
"""
def get_data(file):
	with open(file, "r") as f:
		return(json.load(f))

"""
Write json file data
"""
def set_data(file, data):
	with open(file, "w") as f:
		json.dump(data, f, indent=4, sort_keys=True)

