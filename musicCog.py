import os
import discord
from discord.ext import commands
from pytube import YouTube
import configparser

class MusicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='join')
    async def join(self, ctx):
        is_connected = discord.utils.get(self.bot.voice_clients)

        if not is_connected:
            channel = ctx.author.voice.channel
            await channel.connect()

    @commands.command(name='play')
    async def play(self, ctx, link: str):
        await MusicCommands.join(self, ctx)

        config = configparser.RawConfigParser()
        config.read('config.cfg')
        config_dict = dict(config.items('DMSB_Config'))

        yt = YouTube(link)
        stream = yt.streams.get_by_itag(251)
        stream.download(config_dict['file_path'], config_dict['audio_name'])

        text_channel = self.bot.get_channel(ctx.channel.id)
        await now_playing(text_channel, yt.title)

        voice_client = ctx.message.guild.voice_client
        voice_client.play(discord.FFmpegPCMAudio(executable= config_dict['ffmpeg_exec'], source= os.path.join(config_dict['file_path'], config_dict['audio_name'])))

    @commands.command(name='pause')
    async def pause(self, ctx):
        voice_client = ctx.message.guild.voice_client
        voice_client.pause()

    @commands.command(name='resume')
    async def resume(self, ctx):
        voice_client = ctx.message.guild.voice_client
        voice_client.resume()

async def now_playing(text_channel, title):
    await text_channel.send("Now playing: " + title)

async def setup(bot):
    await bot.add_cog(MusicCommands(bot))