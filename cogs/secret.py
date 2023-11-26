import discord
from discord.ext import commands
import consts

class SecretCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name="confide", aliases=["c"])
	async def anonMsg(self, ctx, *args):
		data = consts.get_data(consts.CONFIDE_DATA)
		sender = self.bot.get_user(ctx.author.id)
		if len(args) == 0:
			await sender.send("Specify a message to send")
			return
		userNum = 0
		if ctx.author.id in data.values():
			for num, id in data.items():
				if id == ctx.author.id:
					userNum = num
					break
		else:
			while True:
				userNum = random.randrange(1000)
				if userNum not in data:
					break
			data.update({str(userNum): ctx.author.id})
		recipient = self.bot.get_user(BARKER) #me
		if not getId(args[0]) is None:
			recipient = self.bot.get_user(getId(args[0]))
			message = list(args)
			message.remove(args[0])
		await recipient.send("Anonymous message from user {}: ".format(userNum) + " ".join(message))
		await sender.send("Anonymous message sent to <@!{}>".format(recipient.id))
		saveData(data, CONFIDE_DATA)

	@commands.command(name="respond", aliases=["reply", "r"])
	async def respondToAnon(self, ctx, userNum:int, *args):
		data = getData(CONFIDE_DATA)
		userId = data.get(str(userNum))
		sender = self.bot.get_user(ctx.author.id)
		if userId == None:
			await sender.send("Couldn't find user with the id {}".format(userId))
		else:
			recipient = bot.get_user(userId)
			await recipient.send("Response from <@!{}>: ".format(userId) + " ".join(args))
			await sender.send("Response sent to <@!{}>".format(recipient.id))

def setup(bot):
	bot.add_cog(SecretCog(bot))
