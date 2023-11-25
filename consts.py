import json
import os

DT_FORMAT = "%m/%d/%Y at %H:00" #01/01/20 01
EMBED_COLOR = 0xe620c1
ACTIVITY_DATA = os.path.abspath('../data/activity.json')


def getData(file):
	with open(file, "r") as f:
		return(json.load(f))

def saveData(data, file): #done
	with open(file, "w") as f:
		json.dump(data, f, indent=4, sort_keys=True)

