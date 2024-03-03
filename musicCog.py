import asyncio
import os
import discord
from discord.ext import commands
from pytube import YouTube
import configparser

class MusicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []
        self.config = configparser.RawConfigParser()
        self.config.read('config.cfg')
        self.config_dict = dict(self.config.items('DMSB_Config'))


    @commands.command(name='join')
    async def join(self, ctx):
        is_connected = discord.utils.get(self.bot.voice_clients)

        if not is_connected:
            channel = ctx.author.voice.channel
            await channel.connect()

    @commands.command(name='play')
    async def play(self, ctx, link: str):
        await MusicCommands.join(self, ctx)
        
        self.queue.append(link)

        if not ctx.voice_client.is_playing():
            play_next(self, ctx)
        else:
            text_channel = self.bot.get_channel(ctx.channel.id)
            await text_channel.send("Song added to queue")

    @commands.command(name='pause')
    async def pause(self, ctx):
        ctx.voice_client.pause()

    @commands.command(name='resume')
    async def resume(self, ctx):
        ctx.voice_client.resume()

    @commands.command(name='skip')
    async def skip(self, ctx): 
        ctx.voice_client.stop()

def play_next(self, ctx):
    if (len(self.queue) > 0):
        yt = YouTube(self.queue[0])
        stream = yt.streams.get_by_itag(251)
        stream.download(self.config_dict['file_path'], self.config_dict['audio_name'], None, False)

        text_channel = self.bot.get_channel(ctx.channel.id)
        self.bot.loop.create_task(text_channel.send("Now playing: " + yt.title))
        
        ctx.voice_client.play(discord.FFmpegPCMAudio(executable= self.config_dict['ffmpeg_exec'], source= os.path.join(self.config_dict['file_path'], self.config_dict['audio_name'])), after=lambda e: play_next(self, ctx))

        self.queue.pop(0)
        
    else:
        ctx.voice_client.stop()

async def setup(bot):
    await bot.add_cog(MusicCommands(bot))