"""
Created by: Alex Barker
Created 11/24/2023
Last edited 11/24/2023

Function: Discord bot with miscellaneous functional features

Features:
	

TODO:
	Message activity (most active, least active, etc)
	Anonymous messaging (?confide, ?respond)
	Play Spotify/YT music in VC
"""

import discord
from discord.ext import commands
from consts import *

tokfile = open("token.txt", "r")
TOKEN = tokfile.readline()
tokfile.close()

def getPrefix(bot, message):
	prefixes = ["!"]
	return prefixes

initialExtensions = [
	"cogs.activity"
]

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=getPrefix, intents=intents, description="A bot that wraps a jukebox and Big Brother into one!")

if __name__ == "__main__":
	for extension in initialExtensions:
		bot.load_extension(extension)
	
bot.remove_command("help")

# run when logging in
@bot.event
async def on_ready():
	print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')
	await bot.change_presence(activity=discord.Game(name="?help"))
	print(f'Successfully logged in!')

@bot.command()
async def help(ctx, *args):
	if len(args) == 0:
		embedVar = discord.Embed(title="Help Menu", description="Use `!help` <command> for more information. Ask @scarome for more help", color=EMBED_COLOR)
		embedVar.add_field(name="1. Server Activity", value="`active`", inline=False)
		await ctx.send(embed=embedVar)
		return
	if args[0] == "!active" or args[0] == "active":
		embedVar = discord.Embed(title="Help Menu: !active", description="See the top 3 most active users", color=EMBED_COLOR)
		embedVar.add_field(name="Usage", value="`!active`", inline=False)
		await ctx.send(embed=embedVar)
		return

bot.run(TOKEN, bot=True, reconnect=True)