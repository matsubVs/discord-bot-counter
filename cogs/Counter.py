import discord
from discord.ext import commands
import os

class Counter(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.guild = None
        self.channel = None


    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.change_presence(status=discord.Status.online, activity=discord.Game('Commands: !help'))
        await self.client.wait_until_ready()
        self.guild = self.client.get_guild(os.getenv('SERVER_ID'))
        print(f'Бот в сети {self.client.user}')
        self.channel = self.guild.get_channel(os.getenv('CHANNEL_ID'))

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.channel.send('Пожалуйста, введите все аргументы команды')


    @commands.Cog.listener()
    async def on_message(self, message: discord.message):
        if message.author.bot:
            return
        if message.channel.id == 963556949021065221:
            await message.channel.send('Sup!')

        try:
            await self.client.process_commands(self, message)
        except TypeError:
            pass


def setup(client):
    client.add_cog(Counter(client))
