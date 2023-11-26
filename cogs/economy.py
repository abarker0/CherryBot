import discord
from discord.ext import commands
from datetime import datetime as dt, timedelta
import random
import consts

class EconomyCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	"""
	Tells the user how many cherries they have
	"""
	@commands.command(name="cherries", aliases=["balance", "bal", "c", "cher"])
	async def get_cherries(self, ctx, user: discord.User=None):
		if not user:
			user = ctx.author
		embed_var = discord.Embed(color=consts.EMBED_COLOR)
		embed_var.add_field(name=":cherries: Cherries :cherries:", value=f"{user.mention}, you have {get_balance(user)} moons", inline=False)
		await ctx.send(embed=embed_var)

	"""
	Collects the users daily cherries, which increases as they maintain a daily streak
	"""
	@commands.command(name="dailycherries", aliases=["daily", "d"])
	async def get_daily_cherries(self, ctx):
		data = consts.get_data(consts.CHERRIES_DATA)
		user = ctx.author
		user_data = data.get(str(user))
		if user_data is None:
			user_data = init_profile()
		
		streak_reset = False
		now = discord.utils.utcnow()
		daily = user_data.get("daily")

		if daily is None:
			daily = (None, 0) # default value allows user to get daily now

		if daily[0] is not None and now < (next_invoke := dt.strptime(user_data.get("daily")[0], consts.DAILY_DT_FORMAT) + timedelta(days=1)): # can't get daily yet
			embedVar = discord.Embed(color=consts.EMBED_COLOR)
			embedVar.add_field(name=":cherries: Daily Cherries :cherries:", value=f"{user.mention}, wait until {dt.strftime(next_invoke, consts.DAILY_DT_FORMAT)} before your next daily", inline=False)
			await ctx.send(embed=embedVar)
			return
		elif now > next_invoke + timedelta(days=1): # past 2 days, lost streak
			streak_reset = True

		current_cherries = get_balance(user)
		user_streak = daily[1] + 1
		added_cherries = calc_daily(user_streak)
		data.update({
				str(user): {
					"cherries": current_cherries + added_cherries,
					"daily": [now.strftime(consts.DAILY_DT_FORMAT), user_streak]
				}
			})
		
		embed_var = discord.Embed(color=consts.EMBED_COLOR)
		if streak_reset:
			embed_text = f"{user.mention} got {added_cherries} cherries! Streak: {user_streak}. \
					Your streak was reset because it's been 48 hours since your last !daily :confused:. \
					Come back tomorrow for {consts.CHERRIES_MULTIPLIER} more!"
		else:
			embed_text = f"{user.mention} got {added_cherries} cherries! Streak: {user_streak}. Come back tomorrow for {consts.CHERRIES_MULTIPLIER} more!"
		embed_var.add_field(name=":cherries: Daily Cherries :cherries:", value=embed_text, inline=False)
		await ctx.send(embed=embedVar)

		consts.set_data(data, consts.CHERRIES_DATA)


	"""
	Transfers cherries from one user to another
	"""
	@commands.command(name="give", aliases=["transfer", "g"])
	async def transfer_cherries(self, ctx, recipient: discord.User=None, cherries: int=1):
		if not recipient:
			return
		
		data = consts.get_data(consts.CHERRIES_DATA)
		user = ctx.author
		user_data = data.get(str(user))
		if user_data is None or (balance := get_balance(user)) < cherries:
			embedVar = discord.Embed(color=consts.EMBED_COLOR)
			embedVar.add_field(name=":cherries: Give Cherries: Fail :cherries:", value=f"{user.mention}, you don't have that many cherries to give. Your current balance is {balance}", inline=False)
			await ctx.send(embed=embedVar)
			return
		else:
			user_data.update({"cherries": balance-cherries})
			if data.get(str(recipient)) == None:
				data.update({
						str(recipient): {
							"moons": givenMoons,
							"daily": [None, 0]
						}
					})
			else:
				currentRecMoons = data.get(str(recipient)).get("moons")
				data.get(str(recipient)).update({"moons": currentRecMoons+givenMoons})
			embedVar = discord.Embed(color=EMBED_COLOR)
			embedVar.add_field(name=":full_moon: Give Moons: Success! :full_moon:", value="<@!{}>, gave {} moons to <@!{}>".format(user, givenMoons, recipient), inline=False)
			await ctx.send(embed=embedVar)
		consts.set_data(data, consts.CHERRIES_DATA)

def set_cherries(user, cherries):
	data = consts.get_data(consts.CHERRIES_DATA)
	data.get(str(user)).update({
		"cherries": getBalance(user)
	})
	consts.set_data(data, consts.CHERRIES_DATA)

def get_balance(user):
	data = consts.get_data(consts.MOONS_DATA)
	user_data = data.get(str(user))
	if user_data is None: #user data doesn't exist
		return 0
	else:
		return user_data.get("cherries")

def calc_daily(streak):
	return consts.CHERRIES_MULTIPLIER * streak

def init_profile():
	return {
		"cherries": 0,
		"daily": (None, 0)
	}

def setup(bot):
	bot.add_cog(EconomyCog(bot))
