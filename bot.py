import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from pytube import YouTube
import configparser

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

discord_intents = discord.Intents.default()
discord_intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=discord_intents, help_command=None)

@bot.event
async def on_ready():
    print('connected')

@bot.command(name='join')
async def join(ctx):
    if not is_connected(bot.voice_clients):
        channel = ctx.author.voice.channel
        await channel.connect()

@bot.command(name='play')
async def play(ctx, link: str):
    await join(ctx)

    config = configparser.RawConfigParser()
    config.read('config.cfg')
    config_dict = dict(config.items('DMSB_Config'))

    yt = YouTube(link)
    stream = yt.streams.get_by_itag(251)
    stream.download(config_dict['file_path'], config_dict['audio_name'])

    text_channel = bot.get_channel(ctx.channel.id)
    await now_playing(text_channel, yt.title)
    
    voice_client = ctx.message.guild.voice_client
    voice_client.play(discord.FFmpegPCMAudio(executable= config_dict['ffmpeg_exec'], source= os.path.join(config_dict['file_path'], config_dict['audio_name'])))

def is_connected(voice_clients):
    voice_client = discord.utils.get(voice_clients)

    if voice_client:
        return True

async def now_playing(text_channel, title):
    await text_channel.send("Now playing: " + title)

bot.run(TOKEN)