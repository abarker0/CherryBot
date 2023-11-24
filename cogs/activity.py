import discord
from discord.ext import commands
from datetime import datetime as dt, timedelta
import random
from consts import *

class ActivityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """
    Listens for new members and broadcasts "Welcome @new_user" in the system channel?
    """
    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send(f'Welcome {member.mention}.')

    """
    Prints the top 3 most active users (by message count)
    """
    @commands.command()
    async def active(self, ctx):
        activity_data = list(getData(ACTIVITY_DATA))
        await ctx.send(f'Top 3 most active users: {activity_data}')

def setup(bot):
    bot.add_cog(ActivityCog(bot))
