import discord
from discord.ext import commands
import datetime
import logging
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
		logging.info(f"Retrieving cherries balance for {user}")
		cherries = get_balance(user)
		embed_var = discord.Embed(color=consts.EMBED_COLOR)
		embed_var.add_field(name=":cherries: Cherries :cherries:", value=f"{user.mention}, you have {cherries} cherries", inline=False)
		await ctx.send(embed=embed_var)
		logging.info(f"Cherries balance of {user} is {cherries}")

	"""
	Collects the users daily cherries, which increases as they maintain a daily streak
	"""
	@commands.command(name="dailycherries", aliases=["daily", "d"])
	async def get_daily_cherries(self, ctx):
		user = ctx.author
		logging.info(f"Collecting daily cherries for {user}")
		streak_reset = False
		now = discord.utils.utcnow()
		logging.info(f"Current time is {now}")
		daily = get_user_data(user, "daily")
		if daily[0] is not None:
			next_invoke = (datetime.datetime.strptime(daily[0], consts.DAILY_DT_FORMAT) + datetime.timedelta(days=1)).replace(tzinfo=datetime.timezone.utc)
			logging.debug(f"Next daily invoke can be done at {next_invoke}")
			if now < next_invoke: # can't get daily yet
				logging.debug(f"Can't get daily yet")
				diff = next_invoke - now
				SECONDS_IN_DAY = 24 * 60 * 60
				SECONDS_IN_HOUR = 60 * 60
				SECONDS_IN_MINUTE = 60
				(hours, r) = divmod(diff.days * SECONDS_IN_DAY + diff.seconds, SECONDS_IN_HOUR)
				(mins, secs) = divmod(r, SECONDS_IN_MINUTE)
				embed_var = discord.Embed(color=consts.EMBED_COLOR)
				embed_var.add_field(name=":cherries: Daily Cherries :cherries:", value=f"{user.mention}, wait {hours} hours, {mins} minutes, and {secs} seconds before your next daily", inline=False)
				await ctx.send(embed=embed_var)
				return
			elif now > next_invoke + datetime.timedelta(days=1): # past 2 days, lost streak
				logging.debug(f"Lost streak because more than 24 hours after last invoke")
				streak_reset = True

		balance = get_user_data(user, "balance")
		user_streak = daily[1] + 1
		added_cherries = calc_daily(user_streak)
		logging.debug(f"Daily added {added_cherries} cherries from a streak of {user_streak} to current balance of {balance}")
		
		embed_var = discord.Embed(color=consts.EMBED_COLOR)
		if streak_reset:
			embed_text = f"{user.mention} got {added_cherries} cherries! Streak: {user_streak}. \
					Your streak was reset because it's been 24 hours since your last !daily :confused:. \
					Come back tomorrow for {consts.CHERRIES_MULTIPLIER} more!"
		else:
			embed_text = f"{user.mention} got {added_cherries} cherries! Streak: {user_streak}. Come back tomorrow for {consts.CHERRIES_MULTIPLIER} more!"
		embed_var.add_field(name=":cherries: Daily Cherries :cherries:", value=embed_text, inline=False)
		await ctx.send(embed=embed_var)

		set_user_data(user, \
				("balance", balance + added_cherries),\
				("daily", (now.strftime(consts.DAILY_DT_FORMAT), user_streak)))

		logging.info(f"Successfully collected daily cherries for {user}")


	"""
	Transfers cherries from one user to another
	"""
	@commands.command(name="give", aliases=["transfer", "g"])
	async def transfer_cherries(self, ctx, recipient: discord.User=None, transferred: int=1):
		if not recipient:
			return

		data = consts.get_data(consts.CHERRIES_DATA)
		user = ctx.author
		logging.info(f"Transferring {transferred} cherries from {user} to {recipient}")
		user_data = data.get(str(user))
		if (balance := get_balance(user)) < transferred: # not enough cherries to give
			logging.debug(f"Failed transferring cherries from {user} to {recipient}, user balance is {balance} which is less than {transferred}")
			embed_var = discord.Embed(color=consts.EMBED_COLOR)
			embed_var.add_field(name=":cherries: Give Cherries: Fail :cherries:", value=f"{user.mention}, you don't have that many cherries to give. Your current balance is {balance}", inline=False)
			await ctx.send(embed=embed_var)
			return

		logging.debug(f"{user} has enough cherries, new balance is {balance - transferred}")
		user_data.update({"cherries": balance - transferred})
		if (recipient_data := data.get(str(recipient))) is None: # recipient doesn't have any data
			data.update({
					str(recipient): {
						"cherries": transferred,
						"daily": [None, 0]
					}
				})
			logging.debug(f"Recipient balance changed from 0 to {transferred}")
		else: # otherwise update their existing data
			recipient_balance = get_balance(recipient)
			recipient_data.update({"cherries": recipient_balance + transferred})
			data.update({str(recipient): recipient_data})
			logging.debug(f"Recipient balance changed from {recipient_balance} to {recipient_balance + transferred}")

		data.update({str(user): user_data})
		embed_var = discord.Embed(color=consts.EMBED_COLOR)
		embed_var.add_field(name=":cherries: Give Cherries: Success! :cherries:", value=f"{user.mention} gave {transferred} cherries to {recipient.mention}", inline=False)
		await ctx.send(embed=embed_var)
		consts.set_data(consts.CHERRIES_DATA, data)
		logging.info(f"Successfully transferred cherries from {user} to {recipient}")

def set_user_data(user, *args):
	data = consts.get_data(consts.CHERRIES_DATA)
	user_data = data.get(str(user))
	if user_data is None:
		user_data = init_profile()
	for (k,v) in args:
		user_data.update({k: v})
	data.update(user_data)
	consts.set_data(consts.CHERRIES_DATA, data)

def get_user_data(user, key):
	data = consts.get_data(consts.CHERRIES_DATA)
	user_data = data.get(str(user))
	if user_data is None:
		user_data = init_profile()
		data.update(user_data)
		consts.set_data(consts.CHERRIES_DATA, data)
	return user_data.get(key)

def calc_daily(streak):
	return consts.CHERRIES_MULTIPLIER * streak

def init_profile():
	return {
		"balance": 0,
		"daily": (None, 0)
	}

async def setup(bot):
	await bot.add_cog(EconomyCog(bot))
