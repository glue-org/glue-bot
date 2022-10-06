import logging
from dotenv import load_dotenv
from glue.discord_bot.bot import Bot
import os
import discord
from discord import app_commands
from glue.discord_bot.groups.project import Project
from pathlib import Path
from typing import Literal, Optional
import base64

# add logging
logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)


# add variable from .env file
path_to_env = Path.cwd() / ".env"
print(f'loading .env file from "{path_to_env}"')
load_dotenv(path_to_env, override=True)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
FRONTEND_URL = os.getenv("FRONTEND_URL")


intents = discord.Intents(guilds=True, members=True)
bot = Bot(intents=intents)

# adding project command group
bot.tree.add_command(Project(bot))


# adding top level command
@bot.tree.command()
@app_commands.guild_only()
@app_commands.default_permissions()
@app_commands.describe(
    logo="Please upload a logo for your project. We recommend svg or png files.",
    theme="Please specify a theme for your project.",
)
async def generate(
    interaction: discord.Interaction,
    logo: Optional[discord.Attachment],
    theme: Optional[
        Literal[
            "light",
            "dark",
            "bumblebee",
            "emerald",
            "corporate",
            "synthwave",
            "retro",
            "cyberpunk",
            "valentine",
            "halloween",
            "garden",
            "forest",
            "aqua",
            "lofi",
            "wireframe",
            "black",
            "luxury",
            "dracula",
            "cmyk",
            "autumn",
            "business",
            "acid",
            "night",
            "winter",
        ]
    ],
):
    """Generates the URL for members to verify with."""
    try:
        await interaction.response.send_message(
            f"❗️The following URL is only valid for the discord server this command was run from!❗️\n"
            f"As a best practice you should create a new channel that contains nothing but this link. Make sure no one but you or people you can trust have the ability to manage that channel!\n\n"
            f"{FRONTEND_URL}/?guild={interaction.guild_id}{f'&logo={base64.b64encode(logo.url.encode()).decode()}' if logo else ''}{f'&theme={theme}' if theme else ''}",
            ephemeral=True,
        )
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}", ephemeral=True)


def run():
    if not path_to_env.exists():
        raise Exception(
            f'.env file at path "{path_to_env}" does not exist. Make sure you create it first. Check the README for more information.'
        )
    print("logging in...")
    if DISCORD_TOKEN:
        bot.run(DISCORD_TOKEN)
    else:
        print("no discord token found. please set DISCORD_TOKEN in .env")


if __name__ == "__main__":
    run()
