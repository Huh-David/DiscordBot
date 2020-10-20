import asyncio
import random

import discord
import os

from discord import Guild, Member
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
def is_not_pinned(mess):
    return not mess.pinned


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


@client.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()


@client.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()


@client.command()
async def play(ctx, args):
    ctx.voice_client.play(discord.FFmpegPCMAudio(source=args), after=None)


@client.command()
async def status(ctx, args=None):
    game = discord.Game(args)
    if args is None:
        await client.change_presence(status=discord.Status.online)  # TODO clear status
    else:
        await client.change_presence(status=discord.Status.online, activity=game)


@client.command()
async def clear(ctx, args="10"):
    if ctx.author.permissions_in(ctx.channel).manage_messages:
        if args.isdigit():
            count = int(args) + 1
            deleted = await ctx.channel.purge(limit=count, check=is_not_pinned)
            await ctx.send('{} messages have been permanently deleted.'.format(len(deleted) - 1))
            await asyncio.sleep(5)
            await ctx.channel.purge(limit=1, check=is_not_pinned)


@client.command()
async def ping(ctx):
    await ctx.send(f'**Pong!** Latency is around __{round(client.latency * 1000)}ms__')


@client.command()
async def credits(ctx):
    embed = discord.Embed(title='Credits for this awesome bot',
                          description='{} wants to know who made this bot'.format(ctx.author.mention),
                          color=0xffaaaa)

    dave = await client.fetch_user(160856702994874368)
    patrick = await client.fetch_user(319152565176762368)
    members = [dave, patrick]

    embed.add_field(name='Dave',
                    value=dave.mention + ' https://github.com/qt1337',
                    inline=True)

    embed.add_field(name='Patrick',
                    value=patrick.mention + ' https://github.com/Mueller-Patrick',
                    inline=True)

    embed.set_thumbnail(url=random.choice(members).avatar_url)
    embed.set_footer(text='These are real cool guys!')
    message = await ctx.send(embed=embed)


@client.command()
async def info(ctx, args=None):
    if args:
        member: Member = discord.utils.find(lambda m: args[1] in m.name, ctx.guild.members)
    else:
        member: Member = ctx.author

    if member:
        embed = discord.Embed(title='Information for {}'.format(member.name),
                              description='This is the user information of {}'.format(member.mention),
                              color=0x22a7f0)
        embed.add_field(name='Joined server at', value=member.joined_at.strftime("%m/%d/%Y, %H:%M:%S"),
                        inline=True)
        embed.add_field(name='Joined discord at', value=member.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
                        inline=True)
        roles = ''
        for role in member.roles:
            if not role.is_default():
                roles += '{} \r\n'.format(role.mention)
        if roles:
            embed.add_field(name='Roles', value=roles, inline=True)
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text='Type "!info" to find informations about yourself.')
        message = await ctx.send(embed=embed)
        await message.add_reaction('💯')
    else:
        ctx.send("I could not find any user with this name!")


client.run(TOKEN)
