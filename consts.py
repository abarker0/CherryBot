import json
import os
from enum import Enum, auto
import logging

logger = logging.getLogger("cherry.consts")

DAILY_DT_FORMAT = r"%m/%d/%Y" #01/01/2020
LOG_DT_FORMAT = r'%Y-%m-%d %H:%M:%S'
EMBED_COLOR = 0xe620c1

LOGGING_CFG_PATH = os.path.abspath('log_cfg.json')

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
	},
	"gambling": {
		"path:": os.path.abspath('data/cherries.json'),
		"init_profile": {
			"blackjack": None
		}
	}
}

CHERRIES_MULTIPLIER = 10

class Coin(Enum):
	HEADS = "heads"
	TAILS = "tails"

	@staticmethod
	def get(val):
		if val in ["h", "heads"]:
			return Coin.HEADS
		elif val in ["t", "tails"]:
			return Coin.TAILS
		return None

class Suit(Enum):
	SPADES = ":spades:"
	HEARTS = ":hearts:"
	DIAMONDS = ":diamonds:"
	CLUBS = ":clubs:"

class Card_Value(Enum):
	ACE = "A"
	TWO = "2"
	THREE = "3"
	FOUR = "4"
	FIVE = "5"
	SIX = "6"
	SEVEN = "7"
	EIGHT = "8"
	NINE = "9"
	TEN = "10"
	JACK = "J"
	QUEEN = "Q"
	KING = "K"

DECK = [(value, suit) for suit in list(Suit) for value in list(Card_Value)]

BLACKJACK_HELP = ":regional_indicator_h: to hit (draw 1 card), :regional_indicator_s: to stand (stop drawing)"

class Blackjack_State(Enum):
	IN_PROGRESS = 0
	STAND = 1
	WIN = 2
	LOSE = 3
	TIE = 4

YDL_OPTIONS = {'format': 'bestaudio'}
FFMPEG_OPTIONS = {'options': '-vn'}
MUSIC_RESULT_COUNT = 10


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
Get user data from a cog's data path, specifying the user and the key. Sets the user's initial profile if it's not found
"""
def get_user_data(data_consts_key, user, key):
	user = str(user)
	key = str(key)
	logger.info(f"Getting {user}'s data for {data_consts_key}")
	if not data_consts_key in DATA_CONSTS.keys():
		logger.error(f"{data_consts_key} is not a valid key in DATA_CONSTS")
		return None
	elif not "path" in (cog_dict := DATA_CONSTS.get(data_consts_key)).keys():
		logger.error(f"'path' key is not defined for DATA_CONSTS key {data_consts_key}")
		return None
	
	data = get_data(cog_dict.get("path"))
	logger.debug(f"Retrieved {data_consts_key} data, got {data}")
	user_data = data.get(user)
	if user_data is None:
		logger.debug(f"Profile for {user} doesn't exist, initializing new profile")
		user_data = DATA_CONSTS.get(data_consts_key).get("init_profile")
		if not "init_profile" in cog_dict.keys():
			logger.error(f"'init_profile' key is not defined for DATA_CONSTS key {data_consts_key}")
			return None
		data.update({user: user_data})
		logger.debug(f"Updated data is {data}")
		set_data(cog_dict.get("path"), data)
	logger.debug(f"Current user data is {user_data}")
	logger.info(f"Successfully got {user}'s data in {data_consts_key} for key {key}: {user_data.get(key)}")
	return user_data.get(key)


"""
Sets user data from a cog's data path, specifying the user and an arbitrary amount of key-value pairs. Sets the user's initial profile if it's not found
"""
def set_user_data(data_consts_key: str, user: str, *args):
	user = str(user)
	logger.info(f"Setting user data for {data_consts_key}")
	if not data_consts_key in DATA_CONSTS.keys():
		logger.error(f"{data_consts_key} is not a valid key in DATA_CONSTS")
		return None
	elif not "path" in (cog_dict := DATA_CONSTS.get(data_consts_key)).keys():
		logger.error(f"'path' key is not defined for DATA_CONSTS key {data_consts_key}")
		return None

	data = get_data(cog_dict.get("path"))
	logger.debug(f"Retrieved {data_consts_key} data, got {data}")
	user_data = data.get(user)
	if user_data is None:
		logger.debug(f"Profile for {user} doesn't exist, initializing new profile")
		user_data = DATA_CONSTS.get(data_consts_key).get("init_profile")
		if not "init_profile" in cog_dict.keys():
			logger.error(f"'init_profile' key is not defined for DATA_CONSTS key {data_consts_key}")
			return None

	logger.debug(f"Initial user data is {user_data}")
	for (k,v) in args:
		k = str(k)
		logger.debug(f"Updating key-value pair ({k}: {v}) for {user}")
		user_data.update({k: v})
	logger.debug(f"Updated user data is {user_data}")
	data.update({user: user_data})
	logger.debug(f"Updated data is {data}")
	set_data(cog_dict.get("path"), data)
	logger.info(f"Successfully set {user}'s data in {data_consts_key}")

