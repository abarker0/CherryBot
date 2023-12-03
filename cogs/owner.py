import discord
from discord.ext import commands
import logging

logger = logging.getLogger("cherry.owner")

class OwnerCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='load', hidden=True)
    @commands.is_owner()
    async def loadCog(self, ctx, cog: str):
        logger.info(f"Loading cog {cog}")
        try:
            await self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            logger.error(f"Failed to load {cog}")
        else:
            await ctx.send('**`SUCCESS`**')
            logger.info(f"Successfully loaded {cog}")

    @commands.command(name='unload', hidden=True)
    @commands.is_owner()
    async def unloadCog(self, ctx, cog: str):
        logger.info(f"Unloading cog {cog}")
        try:
            await self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            logger.error(f"Failed to unload {cog}")
        else:
            await ctx.send('**`SUCCESS`**')
            logger.info(f"Successfully unloaded {cog}")


    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def reloadCog(self, ctx, cog: str):
        logger.info(f"Reloading cog {cog}")
        try:
            await self.bot.unload_extension(cog)
            await self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            logger.error(f"Failed to reload {cog}")
        else:
            await ctx.send('**`SUCCESS`**')
            logger.info(f"Successfully reloaded {cog}")


async def setup(bot):
    await bot.add_cog(OwnerCog(bot))
