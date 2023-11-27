import json
import os
from enum import Enum

DAILY_DT_FORMAT = r"%m/%d/%Y" #01/01/2020
LOG_DT_FORMAT = r'%Y-%m-%d %H:%M:%S'
EMBED_COLOR = 0xe620c1

DATA_CONSTS = {
	"cherries"
}

ACTIVITY_DATA = os.path.abspath('data/activity.json')
CHERRIES_DATA = os.path.abspath('data/cherries.json')
CHERRIES_MULTIPLIER = 10
BALANCE = "balance"
DAILY = "daily"
VALID_ECONOMY_KEYS = [BALANCE, DAILY]


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

def get_user_data(user, key):
	with open(file, )
	data = get_data(consts.CHERRIES_DATA)
	user_data = data.get(str(user))
	if user_data is None:
		user_data = init_profile()
		data.update(user_data)
		consts.set_data(consts.CHERRIES_DATA, data)
	return user_data.get(key)

def set_user_data(user, *args):
	data = consts.get_data(consts.CHERRIES_DATA)
	user_data = data.get(str(user))
	if user_data is None:
		user_data = init_profile()
	for (k,v) in args:
		user_data.update({k: v})
	data.update(user_data)
	consts.set_data(consts.CHERRIES_DATA, data)
