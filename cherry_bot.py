"""
Created by: Alex Barker
Created 11/24/2023
Last edited 11/25/2023

Function: Discord bot with miscellaneous functional features

Features:
	

TODO:
	Message activity (most active, etc)
	Anonymous messaging (confessing to server, anonymous hotline)
	Play Spotify/YT music in VC
	Specific functions for GSO
	Specific functions for UMD (integrate Mercury schedule builder)

"""

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import logging
import logging.handlers
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
bot = commands.Bot(command_prefix=get_prefix, intents=intents, description="A bot that wraps a jukebox and Big Brother into one!")

# run when logging in
@bot.event
async def on_ready():
	print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')
	await bot.change_presence(activity=discord.Game(name="!help"))
	print(f'Successfully logged in!')

@bot.event
async def setup_hook():
	initialExtensions = [
		"cogs.activity",
		"cogs.owner",
		"cogs.economy"
	]
	for extension in initialExtensions:
		await bot.load_extension(extension)

# @bot.command()
# async def help(ctx, *args):
# 	if len(args) == 0:
# 		embedVar = discord.Embed(title="Help Menu", description="Use `!help` <command> for more information. Ask @scarome for more help", color=consts.EMBED_COLOR)
# 		embedVar.add_field(name="1. Server Activity", value="`active`", inline=False)
# 		await ctx.send(embed=embedVar)
# 		return
# 	if args[0] == "!active" or args[0] == "active":
# 		embedVar = discord.Embed(title="Help Menu: !active", description="See the top 3 most active users", color=consts.EMBED_COLOR)
# 		embedVar.add_field(name="Usage", value="`!active`", inline=False)
# 		await ctx.send(embed=embedVar)
# 		return
	
@bot.command()
async def ping(ctx):
	await ctx.send("Pong!")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', consts.LOG_DT_FORMAT, style='{')
handler.setFormatter(formatter)

bot.run(TOKEN, reconnect=True, log_handler=handler)