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
        else:
            logging.warning("Couldn't find a channel to broadcast arrival in")

    """
    Listens for any message and adds it to the activity data for the server
    """
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user or message.guild is None:
            return
        
        logging.info(f"{message.author} sent a message in {message.guild}, updating activity.json")

        user_messages = int(consts.get_user_data("activity", str(message.guild.id), str(message.author)))

        logging.debug(f"{message.author} messages changing from {user_messages} to {user_messages + 1}")
        consts.set_user_data("activity", message.guild, (str(message.author), user_messages + 1))

        logging.info(f"Successfully updated activity.json")

    """
    Prints the top 3 most active users (by message count)
    """
    @commands.command()
    @commands.guild_only()
    async def active(self, ctx):
        logging.info(f"Getting the top 3 most active users in {ctx.guild}")
        top_three_active = sorted(dict(consts.get_data(consts.ACTIVITY_DATA)).items(), reverse=True, key=lambda item: item[1])[:3]
        logging.debug(f"Top three list: {top_three_active}")
        f = lambda i: top_three_active[i][0] if i < len(top_three_active) else "N/A"
        await ctx.send(f'Top 3 most active users: {f(0)}, {f(1)}, {f(2)}')
        logging.info(f"Successfully got the top 3 active users")

async def setup(bot):
    await bot.add_cog(ActivityCog(bot))
