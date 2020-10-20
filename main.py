import asyncio
import random

import discord
import os

from discord import Guild
from discord.ext import commands
from discord.ext.commands import Bot
from discord.voice_client import VoiceClient

TOKEN = os.environ['BOTPASSWORD']
client = commands.Bot(command_prefix='!')


@client.event
async def on_ready():
    print('Bot is online.\n\n')


# Private Methods

# Commands
@client.command()
async def hello(ctx):
    await ctx.send("Hi")


@client.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()


@client.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()


client.run(TOKEN)
