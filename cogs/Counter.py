import os

import discord
from discord.ext import commands
from discord.utils import get
from services.database import DB

session = DB.session


class Counter(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.channel_id = os.getenv("CHANNEL_ID")
        self.server_id = os.getenv("SERVER_ID")
        self.guild = None
        self.channel = None

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.change_presence(
            status=discord.Status.online, activity=discord.Game("Commands: !help")
        )
        await self.client.wait_until_ready()
        self.guild =  self.client.get_guild(self.server_id)
        print(f"Бот в сети {self.client.user}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.channel.send("Пожалуйста, введите все аргументы команды")

    @commands.Cog.listener()
    async def on_message(self, message: discord.message):
        if message.author.bot or message.content.startswith('!'):
            return

        if message.channel.id == int(self.channel_id):
            user_id = message.author.id
            user_name = message.author.name

            user_obj = DB.get_user(str(user_id))
            if user_obj:
                user_obj.messages += 1
                session.add(user_obj)
                session.commit()
                await message.channel.send('member in db')
            else:
                created_user = DB.create_user(user_name, str(user_id))

                await message.channel.send('New member in db')

        try:
            await self.client.process_commands(self, message)
        except TypeError:
            pass

    @commands.command(aliases=['m'])
    async def user_messages(self, ctx) -> None:
        try:
            users = DB.get_all_users()
            for user in users:
                discord_user = get(ctx.guild.members, id=int(user.code))
                if discord_user:
                    await ctx.channel.send(f'{discord_user.mention} отправил {user.messages} сообщений!')
        except Exception as e:
            print(e)


def setup(client):
    client.add_cog(Counter(client))
