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
import consts

tokfile = open("token.txt", "r")
TOKEN = tokfile.readline()
tokfile.close()

# Function from @EvieePy on GitHub
def get_prefix(bot, message):
    """A callable Prefix for our bot. This could be edited to allow per server prefixes."""

    prefixes = ['!']

    # Check to see if we are outside of a guild. e.g DM's etc.
    if not message.guild:
        # Only allow ! to be used in DMs
        return '!'

    # If we are in a guild, we allow for the user to mention us or use any of the prefixes in our list.
    return commands.when_mentioned_or(*prefixes)(bot, message)


intents = discord.Intents.all()
bot = commands.Bot(command_prefix=get_prefix, intents=intents, description="A bot that wraps a jukebox and Big Brother into one!")
	
bot.remove_command("help")

# run when logging in
@bot.event
async def on_ready():
	print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')
	await bot.change_presence(activity=discord.Game(name="!help"))
	print(f'Successfully logged in!')

@bot.event
async def setup_hook():
	initialExtensions = [
		"cogs.activity"
	]
	for extension in initialExtensions:
		await bot.load_extension(extension)

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
	
@bot.command()
async def pong(ctx):
	await ctx.send("Ping!")

bot.run(TOKEN, reconnect=True)