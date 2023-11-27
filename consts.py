import json
import os
from enum import Enum

DAILY_DT_FORMAT = r"%m/%d/%Y" #01/01/2020
LOG_DT_FORMAT = r'%Y-%m-%d %H:%M:%S'
EMBED_COLOR = 0xe620c1

DATA_CONSTS = {
	"activity": {
		"path": os.path.abspath('data/activity.json'),
		"init_profile": {}
	},
	"economy": {
		"path": os.path.abspath('data/cherries.json'),
		"init_profile": {
			"balance": 0,
			"daily": (None, 0)
		}
	}
}

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

"""
Get user data by referencing 
"""
def get_user_data(data_consts_key, user, key):
	data = get_data(DATA_CONSTS.get(data_consts_key).get("path"))
	user_data = data.get(str(user))
	if user_data is None:
		user_data = DATA_CONSTS.get(data_consts_key).get("init_profile")
		data.update(user_data)
		set_data(DATA_CONSTS.get(data_consts_key).get("path"), data)
	return user_data.get(key)

def set_user_data(data_consts_key, user, *args):
	data = get_data(DATA_CONSTS.get(data_consts_key).get("path"))
	user_data = data.get(str(user))
	if user_data is None:
		user_data = DATA_CONSTS.get(data_consts_key).get("init_profile")
	for (k,v) in args:
		user_data.update({k: v})
	data.update(user_data)
	set_data(data_consts_key, data)
