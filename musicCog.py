import pytube.exceptions
import os
import requests
import discord
from discord.ext import commands
from pytube import YouTube, Search, Playlist
from datetime import timedelta
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
            embed_vars = discord.Embed(title= "ERROR", description= "YouTube Url is not valid")   
            await text_channel.send(embed = embed_vars)
            return
        
        if check_if_youtube_url_is_a_playlist(link):
            embed_vars = discord.Embed(description= "Loading playlist")   
            await text_channel.send(embed = embed_vars)
            youtube_playlist = Playlist(link)

            for url in youtube_playlist.video_urls:        
                self.queue.append(YouTube(url))

            embed_vars2 = discord.Embed(description= "Playlist added to queue")    
            await text_channel.send(embed = embed_vars2)
        else:
           self.queue.append(YouTube(link))
           embed_vars = discord.Embed(description= "Song added to queue")
           await text_channel.send(embed = embed_vars)

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
                embed_vars = discord.Embed(title= "Voting", description= "Voting for {0} is cancel".format(query))
                text_channel = self.bot.get_channel(ctx.channel.id)
                await text_channel.send(embed = embed_vars)

    @commands.command(name='pause')
    async def pause(self, ctx):
        ctx.voice_client.pause()

    @commands.command(name='resume')
    async def resume(self, ctx):
        ctx.voice_client.resume()

    @commands.command(name='skip')
    async def skip(self, ctx): 
        ctx.voice_client.stop()

    @commands.command(name="queue")
    async def queue(self, ctx):
        queue_position = 1
        videos_in_queue = ""
        for song in self.queue:
            videos_in_queue += "{0}{1}{2} {3}".format(queue_position, ". ", song.title, str(timedelta(seconds=song.length))) + "\n"
            queue_position = queue_position + 1
            
        embed_vars = discord.Embed(title= "Songs in queue:", description= videos_in_queue)
        text_channel = self.bot.get_channel(ctx.channel.id)   
        await text_channel.send(embed = embed_vars)

def check_if_youtube_url_is_valid(youtube_url):
    youtube_url_formats = ['https://m.youtube.com/', 'https://youtube.com/', 'https://www.youtube.com/', 'https://youtu.be/']

    return any(url_formats in youtube_url for url_formats in youtube_url_formats)

def check_if_youtube_url_is_a_playlist(youtube_url):
    youtube_playlist_keywords = ['playlist', 'list']

    return any (playlist_formats in youtube_url for playlist_formats in youtube_playlist_keywords)

def play_next(self, ctx):
    if (len(self.queue) > 0):
        try:
            video = self.queue[0]
            if not video.age_restricted: 
                stream = video.streams.get_by_itag(251)
                stream.download(self.config_dict['youtube_download_directory'], self.config_dict['download_name'], None, False)

                embed_vars = discord.Embed(title= "Now playing:", description= video.title)
                text_channel = self.bot.get_channel(ctx.channel.id)
                self.bot.loop.create_task(text_channel.send(embed = embed_vars))

                ctx.voice_client.play(discord.FFmpegPCMAudio(executable= self.config_dict['ffmpeg_exec'], source= os.path.join(self.config_dict['youtube_download_directory'], self.config_dict['download_name'])), after=lambda e: play_next(self, ctx))
            else:
                text_channel = self.bot.get_channel(ctx.channel.id)
                embed_vars = discord.Embed(title= "ERROR", description= "{0} is age restricted".format(video.title)) 
                self.bot.loop.create_task(text_channel.send(embed = embed_vars))
            self.queue.pop(0)
            
        except pytube.exceptions.VideoUnavailable:
            text_channel = self.bot.get_channel(ctx.channel.id)
            embed_vars = discord.Embed(title= "ERROR", description= "{0} cannot be loaded".format(self.queue[0])) 
            self.bot.loop.create_task(embed = embed_vars)
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
