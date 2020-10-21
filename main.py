import asyncio
import random
import SQL_Connection as sqlhandler
import SQL_Helper as sqlhelper
import DualisCrawler as dualis
import discord
import os
import youtube_dl

from discord import Guild, Member
from discord.ext import commands, tasks
from ytdl_source import YTDLSource
from discord.ext.commands import Bot
from discord.voice_client import VoiceClient

TOKEN = os.environ['BOTPASSWORD']
client = commands.Bot(command_prefix='!')
queue = []
colors = [discord.Colour.red(), discord.Colour.blue(), discord.Colour.green(), discord.Colour.gold(),
		  discord.Colour.orange(), discord.Colour.purple(), discord.Colour.blurple(),
		  discord.Colour.dark_blue(),
		  discord.Colour.teal(), discord.Colour.magenta()]


@client.event
async def on_ready():
	print('Bot is online.\n\n')


#    change_status.start()


# @tasks.loop(seconds=5.0)
# async def change_status():
#     await client.change_presence(activity=discord.Game(name='Listening to music'), status=discord.Status.online)
#     await asyncio.sleep(5)
#
#     # TODO change color of funny llama role


# Private Methods
def is_not_pinned(mess):
	return not mess.pinned


def is_supported(url):
	extractors = youtube_dl.extractor.gen_extractors()
	for e in extractors:
		if e.suitable(url) and e.IE_NAME != 'generic':
			return True
	return False


async def play_youtube_song(ctx):
	async with ctx.typing():
		player = await YTDLSource.from_url(queue[0], loop=client.loop)
		ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

	await ctx.send('**Now playing:** {}'.format(player.title))
	del (queue[0])


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
async def play(ctx, args="nourl"):
	if is_supported(args):
		global queue
		queue = [args]

		voice_channel = ctx.author.voice.channel
		await voice_channel.connect()

		await play_youtube_song(ctx)

	else:
		await ctx.author.voice.channel.connect()
		ctx.voice_client.play(discord.FFmpegPCMAudio(source="alarm.mp3"), after=None)
		await ctx.send(f"{args} is not a valid YouTube URL!")
		ctx.voice_client.disconnect()


@client.command()
async def skip(ctx):
	ctx.message.guild.voice_client.stop()
	await play_youtube_song(ctx)


@client.command()
async def pause(ctx):
	server = ctx.message.guild
	voice_channel = server.voice_client

	voice_channel.pause()


@client.command()
async def stop(ctx):
	server = ctx.message.guild
	voice_channel = server.voice_client

	voice_channel.stop()


@client.command()
async def resume(ctx):
	server = ctx.message.guild
	voice_channel = server.voice_client

	voice_channel.resume()


@client.command()
async def view(ctx):
	await ctx.send(f'Your queue is now `{queue}!`')


@client.command()
async def queue(ctx, args):
	global queue

	if is_supported(args):
		queue.append(args)
		await ctx.send(f'`{args}` added to queue!')
	else:
		await ctx.send(f"{args} is not a valid YouTube URL!")


@client.command()
async def remove(ctx, number):
	global queue

	try:
		del (queue[int(number)])
		await ctx.send(f'Your queue is now `{queue}!`')

	except ValueError:
		await ctx.send('Your queue is either **empty** or the index is **out of range**')


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


@client.command()
async def grade(ctx, *args):
	argsString = '{}'.format(' '.join(args))
	loop = asyncio.get_event_loop()
	task = loop.create_task(
		asyncGradeCoroutine(ctx, argsString)
	)


async def asyncGradeCoroutine(ctx, argsString):
	status = await dualis.grade_available(argsString)
	await ctx.send(status)


@client.event
async def on_voice_state_update(member, before, after):
	if before.channel is None and after.channel is not None and member.id == 237250199175561216:
		await member.edit(deafen=True)

		voice_channel = member.voice.channel
		voice_client = await voice_channel.connect()

		voice_client.play(source=discord.FFmpegPCMAudio(source='alarm.mp3'))

		await asyncio.sleep(4)
		await member.edit(deafen=False)
		await voice_client.disconnect()


# Increase the message counter of a user every time he sends a message
@client.event
async def on_message(message):
	sqlhelper.increaseMessageCounter(message.author, message.author.id)
	await client.process_commands(message)


client.run(TOKEN)
