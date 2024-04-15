import asyncio
import os
import requests
import discord
from discord.ext import commands
from pytube import YouTube, Search, Playlist
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

        text_channel = self.bot.get_channel(ctx.channel.id)

        if not check_if_youtube_url_is_valid(link):
            await text_channel.send("YouTube Url is not valid")
            return
        
        if check_if_youtube_url_is_a_playlist(link):
            await text_channel.send("Loading playlist...")
            youtube_playlist = Playlist(link)

            for url in youtube_playlist.video_urls:        
                self.queue.append(url)        
                
            await text_channel.send("Playlist added to queue")
        else:
           await text_channel.send("Song added to queue")

        if not ctx.voice_client.is_playing():
                play_next(self, ctx)

    @commands.command(name='search')
    async def search(self, ctx, *query: str):
        search = Search(query)    
        await add_reaction_buttons(self, ctx, search.results[:5])
        reaction_emoji = await get_reaction(self, ctx)

        match reaction_emoji:
            case "1️⃣": 
                await MusicCommands.play(self, ctx, search.results[0].watch_url)
            case "2️⃣":
                await MusicCommands.play(self, ctx, search.results[1].watch_url)
            case "3️⃣": 
                await MusicCommands.play(self, ctx, search.results[2].watch_url)
            case "4️⃣": 
                await MusicCommands.play(self, ctx, search.results[3].watch_url)
            case "5️⃣":
                await MusicCommands.play(self, ctx, search.results[4].watch_url)
            case _:
                text_channel = self.bot.get_channel(ctx.channel.id)
                await text_channel.send("Voting for {0} is cancel".format(query))

    @commands.command(name='pause')
    async def pause(self, ctx):
        ctx.voice_client.pause()

    @commands.command(name='resume')
    async def resume(self, ctx):
        ctx.voice_client.resume()

    @commands.command(name='skip')
    async def skip(self, ctx): 
        ctx.voice_client.stop()

def check_if_youtube_url_is_valid(youtube_url):
    youtube_url_formats = ['http://m.youtube.com/', 'http://youtube.com/', 'https://www.youtube.com/', 'https://youtu.be/']

    if not any(url_formats in youtube_url for url_formats in youtube_url_formats):
        return False

    request = requests.get(youtube_url, allow_redirects=False)
    return request.status_code == 200

def check_if_youtube_url_is_a_playlist(youtube_url):
    youtube_playlist_keywords = ['playlist', 'list']

    if any (playlist_formats in youtube_url for playlist_formats in youtube_playlist_keywords):
        return True

def play_next(self, ctx):
    if (len(self.queue) > 0):
        yt = YouTube(self.queue[0])
        if not yt.age_restricted: 
            stream = yt.streams.get_by_itag(251)
            stream.download(self.config_dict['file_path'], self.config_dict['audio_name'], None, False)

            text_channel = self.bot.get_channel(ctx.channel.id)
            self.bot.loop.create_task(text_channel.send("Now playing: " + yt.title))

            ctx.voice_client.play(discord.FFmpegPCMAudio(executable= self.config_dict['ffmpeg_exec'], source= os.path.join(self.config_dict['file_path'], self.config_dict['audio_name'])), after=lambda e: play_next(self, ctx))
        else:
            text_channel = self.bot.get_channel(ctx.channel.id)
            self.bot.loop.create_task(text_channel.send("This video is age restricted"))
        self.queue.pop(0)
    else:
        ctx.voice_client.stop()

async def add_reaction_buttons(self, ctx, searchResults):
    text_channel = self.bot.get_channel(ctx.channel.id)
    voting_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]

    message = await text_channel.send('Vote to select song: \n1. {0} \n2. {1} \n3. {2} \n4. {3} \n5. {4}'.format(searchResults[0].title, searchResults[1].title, searchResults[2].title, searchResults[3].title, searchResults[4].title) )
    for emoji in range(len(voting_emojis)):
        await message.add_reaction(voting_emojis[emoji])

async def get_reaction(self, ctx):
    def check_for_reaction (reaction, user):
        return user == ctx.author and reaction.emoji
    
    try:
        reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check_for_reaction)
        return reaction.emoji

    except TimeoutError:
        pass
    
async def setup(bot):
    await bot.add_cog(MusicCommands(bot))
