import discord

from discord.ext import commands
from discord.ext.commands import Bot
from discord.voice_client import VoiceClient

# local imports
import credentials

TOKEN = credentials.token
client = commands.Bot(command_prefix='!')


@client.event
async def on_ready():
    print('Bot is online.\n\n')


client.run(TOKEN)
