from discord.ext import tasks
from discord import app_commands
from discord import Guild
import discord
from glue.database.database import Guilds
from glue.discord_bot.helpers import verify_ownership_for_guild
from dotenv import load_dotenv
import os
import time
import asyncio
import logging

load_dotenv(override=True)
MODE = os.getenv("MODE")
TEST_GUILD_ID = os.getenv("TEST_GUILD_ID")

# create logger
logger = logging.getLogger("discord")

# initialize DB
db = Guilds()


class Bot(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    # In this basic example, we just synchronize the app commands to one guild.
    # Instead of specifying a guild to every command, we copy over our global commands instead.
    # By doing so, we don't have to wait up to an hour until they are shown to the end-user.
    async def setup_hook(self):
        # This copies the global commands over to your guild for development.
        if MODE == "development":
            if not TEST_GUILD_ID:
                raise Exception("TEST_GUILD_ID not set in .env")
            MY_GUILD = discord.Object(id=TEST_GUILD_ID)
            self.tree.copy_global_to(guild=MY_GUILD)
            await self.tree.sync(guild=MY_GUILD)

        else:
            await self.tree.sync()

        # to add a cog do the following
        # self.add_cog()

    @tasks.loop(seconds=60 * 60)
    async def check_ownership(self):
        logger.info("Checking ownership")
        result = await asyncio.gather(
            *[verify_ownership_for_guild(guild, self) for guild in db.get_guilds()]
        )
        logger.info("Done checking ownership")

    async def on_ready(self):
        print(f"We have logged in as {self.user}.")
        # this has to be callled here instead of in setup_hook because it needs to be called after the bot is logged in
        self.check_ownership.start()

    # called when bot is added to guild
    async def on_guild_join(self, guild: Guild):
        # get the owner of a guild, this needs the "members" intent
        owner = guild.owner
        # send a message to the owner if it exists
        if owner:
            await owner.send(
                embed=discord.Embed(
                    title=f"Hey there, thanks for having me 🥳\n",
                    description=f"If you want to setup an NFT project to grant holder roles to members, run the `/project add` command in any channel of the respective server.\n"
                    f"After you setup your first project, you can run `/generate` to generate your unique verification URL 😊\n\n"
                    f"🚨 **FAQ - READ FIRST** 🚨\n\n"
                    f"1️⃣ when specifying a role to grant, make sure you simpy use the role's name, don't `@` it!\n"
                    f"　　- 👼 good: `mySuperCrazyRole`\n"
                    f"　　- 👻 bad: `@mySuperCrazyRole`\n"
                    f"2️⃣ make sure the bots role (`glue.bot`) is always **above** the roles it should manage in your discord server's setting (see picture below)!"
                    f"3️⃣ if your users can't verify themselves, this has likely two reasons:\n"
                    f"　　- the user doesn't have cookies in his browser enabled\n"
                    f"　　- the user opens the page in the discord browser, not the device browser if on mobile. Make sure they click on the bottom right browser icon to open the page in the device browser!\n\n"
                    f"If you're still not sure how to setup glue, check this [guide](https://youtu.be/xWmVfiRyYns?t=250) 📚\n\n",
                ).set_image(url="https://imgur.com/vThlbIi.png")
            )
