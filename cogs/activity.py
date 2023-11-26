import discord
from discord.ext import commands
import logging
import consts

class ActivityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """
    Listens for new members and broadcasts "Welcome @new_user" in the system channel
    """
    @commands.Cog.listener()
    async def on_member_join(self, member):
        logging.info(f"{member.author} just joined {member.guild}")
        channel = member.guild.system_channel
        if channel is not None:
            logging.info(f"Broadcasting their arrival in {member.guild.system_channel}")
            await channel.send(f'Welcome {member.mention}.')

    """
    Listens for any message and adds it to the activity data for the server
    """
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user or message.guild is None:
            return
        
        logging.info(f"{message.author} sent a message in {message.guild}, updating activity.json")

        activity_data = consts.get_data(consts.ACTIVITY_DATA) # gets the entire json in dict format
        logging.debug(f"Activity data: {activity_data}")

        guild_data = activity_data.get(str(message.guild.id)) # gets the dict for the guild (server)
        if guild_data is None:
            logging.debug(f"Didn't find guild data, initializing new data")
            guild_data = {}
        logging.debug(f"Guild data: {guild_data}")

        user_data = guild_data.get(str(message.author)) # gets the number of messages sent by the user in the guild
        if user_data is None:
            logging.debug(f"Didn't find user data, initializing new data")
            user_data = 0
        logging.debug(f"Current user data: {user_data}")

        guild_data.update({str(message.author): user_data + 1}) # updates the guild data with the new user data
        logging.debug(f"Updated guild data (with increment): {guild_data}")

        activity_data.update({str(message.guild.id): guild_data}) # updates all the data with the new guild data
        logging.debug(f"Update activity data: {activity_data}")

        consts.set_data(consts.ACTIVITY_DATA, activity_data) # pushes all the data back into the file
        logging.info(f"Successfully updated activity.json")

    """
    Prints the top 3 most active users (by message count)
    """
    @commands.command()
    @commands.guild_only()
    async def active(self, ctx):
        logging.info(f"Getting the top 3 most active users in {ctx.guild}")
        top_three_active = sorted(dict(consts.get_data(consts.ACTIVITY_DATA)).items(), reverse=True, key=lambda item: item[1])[:3]
        f = lambda i: top_three_active[i][0] if i < len(top_three_active) else "N/A"
        await ctx.send(f'Top 3 most active users: {f(0)}, {f(1)}, {f(2)}')

async def setup(bot):
    await bot.add_cog(ActivityCog(bot))
