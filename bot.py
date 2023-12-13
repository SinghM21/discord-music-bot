import discord
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')

client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    print('connected')

client.run(TOKEN)