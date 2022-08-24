from discord import app_commands
import discord
from ic import Principal
from glue.database.database import Guilds
from glue.discord_bot.ui.button import Button
from glue.discord_bot.ui.select import DropdownView
from glue.discord_bot.ui.modal import Questionnaire
from typing import Literal, Optional
from glue.database.database import GlueGuild

# connection to database
db = Guilds()


class Project(app_commands.Group):
    """Manage general commands"""

    def __init__(self, client: discord.Client):
        super().__init__()
        self.client = client

    @app_commands.command()
    @app_commands.describe(
        name='Please provide a name for your project. This will only be used internally',
        canister_id='Please specify the projects canister ID, e.g. `pk6rk-6aaaa-aaaae-qaazq-cai`',
        standard='Please pick the standard the canister is implementing.',
        role='Please specify the name of the role that users will receive when they are holders.',
    )
    @app_commands.guild_only()
    @app_commands.default_permissions()
    async def add(self, interaction: discord.Interaction, name: str, canister_id: str, standard: Literal['ext', 'dip721', 'ogy', 'icp-ledger', 'ccc', 'icrc-1'], role: str):
        """Set up an NFT project"""
        try:
            # check if the canister id provided is valid
            Principal.from_str(canister_id)

            if interaction.guild and interaction.guild_id:
                db.create_guild(guild_id=str(
                    interaction.guild_id), canister_id=canister_id, token_standard=standard, role=role, name=name)
                await interaction.guild.create_role(name=role)
                await interaction.response.send_message(f'Added project _{name}_ to database', ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f'Error: {e}', ephemeral=True)

    @app_commands.command()
    @app_commands.guild_only()
    @app_commands.default_permissions()
    async def list(self, interaction: discord.Interaction):
        """List all projects"""
        guild: Optional[GlueGuild] = db.get_guild_by_id(
            str(interaction.guild_id))
        if not guild or not guild['canisters']:
            await interaction.response.send_message('No projects found', ephemeral=True)
        else:
            messages = []
            for project in guild['canisters']:
                messages.append(discord.Embed(
                    title=f'{project["name"]}', description=f'📇 **name:** {project["name"]}\n🪪 **canister id:** {project["canisterId"]}\n🕵🏿‍♂️ **role:** {project["role"]}\n💾 **standard:** {project["tokenStandard"]}\n\n'))
            await interaction.response.send_message(embeds=messages, ephemeral=True)

    @ app_commands.command()
    @ app_commands.guild_only()
    @ app_commands.default_permissions()
    @ app_commands.describe(
        canister_id='Please specify the canister ID of the project you want to delete, e.g. `pk6rk-6aaaa-aaaae-qaazq-cai`',
    )
    async def remove(self, interaction: discord.Interaction, canister_id: str):
        """Remove a project"""
        try:
            db.delete_canister(str(interaction.guild_id), canister_id)
            await interaction.response.send_message(ephemeral=True, embed=discord.Embed(title='Removed project', description=f'Removed project __{canister_id}__ from database.'))
        except Exception as e:
            await interaction.response.send_message(f'Error: {e}', ephemeral=True)

    # @app_commands.command()
    # async def modal(self, interaction: discord.Interaction):
    #     """open modal"""
    #     await interaction.response.send_modal(Questionnaire())

    # @app_commands.command()
    # async def button(self, interaction: discord.Interaction):
    #     """open button"""
    #     await interaction.response.send_message("moin", view=Button())

    # @app_commands.command()
    # async def select(self, interaction: discord.Interaction):
    #     """open select"""
    #     await interaction.response.send_message("moin", view=DropdownView())
