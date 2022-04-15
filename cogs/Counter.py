import os

import discord
from discord.ext import commands
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
                await message.channel.send('Member in db')
            else:
                created_user = DB.create_user(user_name, str(user_id))

                await message.channel.send('New member in db')

        try:
            await self.client.process_commands(self, message)
        except TypeError:
            pass

    @commands.command(aliases=['m'])
    async def user_messages(self, ctx, member: discord.Member = None) -> None:
        if not member:
            users = DB.get_all_users()
            message = ''
            for user in users:
                message += f'{user.name} отправил {user.messages} сообщений!\n'

            await ctx.author.send(message)
        else:
            user = DB.get_user(str(member.id))

            message = ''
            if user:
                message += f'{user.name} отправил {user.messages} сообщений!'
            else:
                message += 'Пользователь не найден!'

            await ctx.author.send(message)


def setup(client):
    client.add_cog(Counter(client))
