import os

import discord
from discord.ext import commands
from discord.utils import get
from services.database import DB
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from pytz import timezone

session = DB.session


class Counter(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.channel_id = os.getenv("CHANNEL_ID")
        self.server_id = os.getenv("SERVER_ID")
        self.guild = None
        self.scheduler = AsyncIOScheduler()

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.change_presence(
            status=discord.Status.online, activity=discord.Game("Commands: !help")
        )
        await self.client.wait_until_ready()

        self.scheduler.add_job(
            self.user_messages,
            CronTrigger(
                day_of_week=6,
                hour=14,
                minute=0,
                second=0,
                timezone=timezone("Europe/Moscow"),
            ),
        )
        self.scheduler.start()

        print("scheduler set up")
        print(self.scheduler)
        self.guild = self.client.get_guild(int(self.server_id))
        print(f"Бот в сети {self.client.user}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.channel.send("Пожалуйста, введите все аргументы команды")

    @commands.Cog.listener()
    async def on_message(self, message: discord.message):
        if message.author.bot or message.content.startswith("!"):
            return

        if message.channel.id == int(self.channel_id):
            user_id = message.author.id
            user_name = message.author.name

            user_obj = DB.get_user(str(user_id))
            if user_obj:
                user_obj.messages += 1
                session.add(user_obj)
                session.commit()
            else:
                created_user = DB.create_user(user_name, str(user_id))

        try:
            await self.client.process_commands(self, message)
        except TypeError:
            pass

    async def user_messages(self) -> None:
        channel = self.client.get_channel(int(os.getenv("CHANNEL_ID")))

        try:
            users = DB.get_all_users()
            message = ""
            for user in users:
                discord_user = get(self.guild.members, id=int(user.code))
                if discord_user:
                    message += f"{discord_user.mention} -`{user.messages}`\n"

            await channel.send(message)
        except Exception as e:
            print(e)


def setup(client):
    client.add_cog(Counter(client))
