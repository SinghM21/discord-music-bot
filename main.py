import asyncio
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

discord_intents = discord.Intents.default()
discord_intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=discord_intents, help_command=None)

@bot.event
async def on_ready():
    print('connected')

async def main():
    async with bot:
        await bot.load_extension("musicCog")
        await bot.start(TOKEN)

asyncio.run(main())