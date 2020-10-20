import discord
import os

from discord.ext import commands
from discord.ext.commands import Bot
from discord.voice_client import VoiceClient

TOKEN = os.environ['BOTPASSWORD']
client = commands.Bot(command_prefix='!')


@client.event
async def on_ready():
    print('Bot is online.\n\n')


client.run(TOKEN)
