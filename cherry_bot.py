"""
Created by: Alex Barker
Created 11/24/2023
Last edited 11/25/2023

Function: Discord bot with miscellaneous functional features

Features:
	Message activity (tracks user messages, displays top three most active users in the server)
	Economy functions (getting balance, collecting daily currency, transferring funds, integration with gambling functions)
	Gambling functions (play 50-50 coin flip, play blackjack)
	
TODO:
	Anonymous messaging (confessing to server, anonymous hotline)
	Play Spotify/YT music in VC
	Specific functions for GSO
	Specific functions for UMD (integrate Mercury schedule builder)
	Pokemon
"""

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import logging
import logging.config
import consts

load_dotenv()
TOKEN = os.getenv('TOKEN')

# Function from @EvieePy on GitHub
def get_prefix(bot, message):

    prefixes = ['!']

    # Check to see if we are outside of a guild. e.g DM's etc.
    if not message.guild:
        # Only allow ! to be used in DMs
        return '!'

    # If we are in a guild, we allow for the user to mention us or use any of the prefixes in our list.
    return commands.when_mentioned_or(*prefixes)(bot, message)


intents = discord.Intents.all()
bot = commands.Bot(command_prefix=get_prefix, intents=intents, description="A bot that wraps a jukebox and Big Brother into one!", help_command=None)

# run when logging in
@bot.event
async def on_ready():
	print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')
	await bot.change_presence(activity=discord.Game(name="!help"))
	print(f'Successfully logged in!')

@bot.event
async def setup_hook():
	initialExtensions = [
		# "cogs.activity",
		"cogs.owner",
		"cogs.economy",
		"cogs.gambling",
		"cogs.music"
	]
	for extension in initialExtensions:
		await bot.load_extension(extension)

@bot.command()
async def help(ctx, *args):
	if len(args) == 0:
		embed = discord.Embed(title="Help Menu", description="Use `!help` <command> for more information. Ask @scarome for more help", color=consts.EMBED_COLOR)
		embed.add_field(name="1. Server Activity", value="`active`", inline=False)
		embed.add_field(name="2. Economy", value="`balance`, `daily`, `give`", inline=False)
		await ctx.send(embed=embed)
		return
	if args[0] == "!active" or args[0] == "active":
		embed = discord.Embed(title="Help Menu: !active", description="See the top 3 most active users", color=consts.EMBED_COLOR)
		embed.add_field(name="Usage", value="`!active`", inline=False)
		await ctx.send(embed=embed)
		return
	
@bot.command()
async def ping(ctx):
	cherry_logger.info("Ping command called")
	await ctx.send("Pong!")


logging.config.dictConfig(consts.get_data(consts.LOGGING_CFG_PATH))
logger = logging.getLogger('discord')
cherry_logger = logging.getLogger("cherry")

bot.run(TOKEN, reconnect=True)