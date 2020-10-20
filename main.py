import asyncio
import random

import discord
import os

from discord import Guild
from discord.ext import commands
from discord.ext.commands import Bot
from discord.voice_client import VoiceClient
import SQL_Connection as sqlhandler

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
async def saveToSQL(ctx, *args):
	argsString = '{}'.format(' '.join(args))
	conn = sqlhandler.getConnection()
	cur = conn.cursor()
	query = """INSERT INTO test (name, time) VALUES (%s, now())"""
	cur.execute(query, (argsString,))
	conn.commit()
	cur.close()
	await ctx.send('Saved your Message "{}" to SQL! Jippieeeeee'.format(argsString))


client.run(TOKEN)
