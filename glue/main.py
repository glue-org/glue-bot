import logging
from dotenv import load_dotenv
from glue.discord_bot.bot import Bot
import os
import discord
from discord import app_commands
from glue.discord_bot.groups.project import Project

# add logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


# add variable from .env file
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
FRONTEND_URL = os.getenv('FRONTEND_URL')


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = Bot(intents=intents)

# adding project command group
bot.tree.add_command(Project(bot))


# adding top level command
@bot.tree.command()
@app_commands.guild_only()
@app_commands.default_permissions()
async def generate(interaction: discord.Interaction):
    """Generates the URL for members to verify with."""
    try:
        await interaction.response.send_message(f'❗️The following URL is only valid for the discord server this command was run from!❗️\n'
                                                f'As a best practice you should create a new channel that contains nothing but this link. Make sure no one but you or people you can trust have the ability to manage that channel!\n\n'
                                                f'{FRONTEND_URL}/?guild={interaction.guild_id}',
                                                ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f'Error: {e}', ephemeral=True)

if __name__ == '__main__':
    print("logging in...")
    if DISCORD_TOKEN:
        bot.run(DISCORD_TOKEN)
    else:
        print("no discord token found. please set DISCORD_TOKEN in .env")
