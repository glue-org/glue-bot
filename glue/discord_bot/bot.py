from discord.ext import tasks
from discord.ext import commands
from discord import Guild
import discord
from glue.database.database import Guilds
from glue.discord_bot.helpers import verify_ownership_for_guild

TEST_GUILD_ID = "974261271857860649"  # replace with your guild id

MY_GUILD = discord.Object(id=TEST_GUILD_ID)

# initialize DB
db = Guilds()


class Bot(commands.Bot):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents, command_prefix="")

    # In this basic example, we just synchronize the app commands to one guild.
    # Instead of specifying a guild to every command, we copy over our global commands instead.
    # By doing so, we don't have to wait up to an hour until they are shown to the end-user.
    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)
        self.check_ownership.start()

        # to add a cog do the following
        # self.add_cog()

    # loop
    @tasks.loop(seconds=10)
    async def check_ownership(self):
        for guild in db.get_guilds():
            verify_ownership_for_guild(guild)

    async def on_ready(self):
        print(f"We have logged in as {self.user}.")

    # called when bot is added to guild
    async def on_guild_join(self, guild: Guild):
        # get the owner of a guild, this needs the "members" intent
        owner = guild.owner
        # send a message to the owner if it exists
        if owner:
            await owner.send(
                f"Hey there, thanks for having me 🥳\n"
                f"If you want to setup an NFT project to grant holder roles to members, run the `/project add` command in any channel of the respective server.\n"
                f"After you setup your first project, you can run `/generate` to generate your unique verification URL 😊\n"
            )

    # on_message event is called when a message is sent
    # async def on_message(self, message):
    #     # ignore our own messages
    #     if message.author == self.user:
    #         return

    #     if message.content.startswith('$hello'):
    #         await message.channel.send('Hello!')
