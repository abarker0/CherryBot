import discord
from discord.ext import commands
import logging
import yt_dlp
import requests
import consts
import asyncio

logger = logging.getLogger("cherry.music")

class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """
    Joins the user's voice channel
    """
    @commands.command(name="join", aliases=["j"])
    async def join(self, ctx):
        user = ctx.author
        logger.info(f"Trying to join {user}'s voice channel")
        if user.voice:
            channel = user.voice.channel
            logger.debug(f"Joining {user} in {channel}.")
            await channel.connect()
            logger.info(f"Successfully joined {user} in {channel}")
        else:
            logger.info(f"Failed to join, {user} not in voice channel.")
            await ctx.send(f"{user.mention}, you need to be connected to a voice channel.")

    """
    Leaves the current voice channel in the guild
    """
    @commands.command(name="leave", aliases=["l"])
    async def leave(self, ctx):    
        voice_client = ctx.message.guild.voice_client
        logger.info(f"Trying to leave my voice channel")
        if voice_client and voice_client.is_connected():
            logger.info(f"Leaving voice channel.")
            await voice_client.disconnect()
            logger.info(f"Successfully left voice channel")
        else:
            logger.info(f"Failed to leave, I'm not in voice channel.")
            await ctx.send("I'm not in a voice channel.")

    """
    Play a Youtube URL. If the url is not valid, searches for the top 10 results and displays them, which the user can choose from to play.
    If already playing, stops the current track and plays the given one. If paused, resumes playing.
    """
    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx, *args):
        voice_client = ctx.message.guild.voice_client

        if len(args) == 0:
            if voice_client and voice_client.is_connected() and voice_client.is_paused():
                logger.info(f"Resuming music in {ctx.message.guild}")
                voice_client.resume()
            else:
                logger.info(f"Can't play music without a url or search query")
                await ctx.send("Please provide a url to play or search terms")
            return
        
        if not voice_client or not voice_client.is_connected():
            MusicCog.join(ctx)
            
        arg = " ".join(args)
        with yt_dlp.YoutubeDL(consts.YDL_OPTIONS) as ydl:
            try:
                requests.get(arg) # see if valid url by sending GET request
            except: # invalid url, search for top results
                videos = ydl.extract_info(f"ytsearch:{arg}", download=False)['entries'][0:consts.MUSIC_RESULT_COUNT]
                print(videos)
            else: # valid url, play music directly
                logger.info(f"Playing {arg} in {ctx.guild}.")

                result = ydl.extract_info(arg, download=False)
                if "entries" in result: # given a playlist, clarify with user whether adding entire playlist or just the song
                    logger.debug(f"Given a playlist, checking with user whether to queue playlist or not")
                    embed = discord.Embed(title=":notes: Music Player :notes:", description="Found playlist, queue full playlist or play given song?", color=consts.EMBED_COLOR)
                    embed.add_field(name="Playlist content:", value="", inline=False)
                    msg = await ctx.send(embed=embed)

                    def check(reaction, user):
                        logger.debug(f"Received {reaction}, {user} from music play input check")
                        return user == ctx.author and str(reaction) in ["\N{Regional Indicator Symbol Letter Y}", "\N{Regional Indicator Symbol Letter N}"]
                    await msg.add_reaction("\N{Regional Indicator Symbol Letter Y}")
                    await msg.add_reaction("\N{Regional Indicator Symbol Letter N}")
                    try:
                        logger.debug("Adding reactions and waiting for player input")
                        reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
                    except asyncio.TimeoutError:
                        logger.debug(f"Timed out: automatically playing song instead of queuing playlist")
                    else:
                        if str(reaction) == "\N{Regional Indicator Symbol Letter Y}":
                            logger.debug(f"Queuing playlist")
                            queue(result['entries]'][1:])
                    video = result['entries'][0]
                else:
                    # Just a video
                    video = result

                logger.debug(f"Song info for {arg} is {video}")
                
                if voice_client.is_playing():
                    voice_client.stop()
                    logger.debug(f"Stopped current song")
                voice_client.play(discord.FFmpegPCMAudio(video["url"], **consts.FFMPEG_OPTIONS))
            logger.info(f"Successfully playing {arg} in {ctx.guild}")
    
    @commands.command(name="pause")
    async def pause(self, ctx):
        logger.info(f"Pausing music in {ctx.message.guild}")
        voice_client = ctx.message.guild.voice_client
        if voice_client and voice_client.is_connected() and voice_client.is_playing():
            voice_client.pause()
            logger.info(f"Paused music in {ctx.message.guild}")
        else:
            logger.info(f"Can't pause music, nothing is playing")
        

async def setup(bot):
    await bot.add_cog(MusicCog(bot))
