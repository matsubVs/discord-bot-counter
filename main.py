import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from cogs import Counter

import discord

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

load_dotenv()


client = commands.Bot(command_prefix='!', intents=intents)
client.remove_command('help')


@client.command()
async def users(ctx):
    await ctx.channel.send(f"""Количество участников: {client.get_guild(int(os.getenv('SERVER_ID'))).member_count}""")


Counter.setup(client)
client.run(os.getenv('D_TOKEN'), bot=True)