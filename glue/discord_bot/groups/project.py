from discord import Guild, app_commands
import discord
from glue.database.database import Database
from glue.discord_bot.ui.button import Button
from glue.discord_bot.ui.select import DropdownView
from glue.discord_bot.ui.modal import Questionnaire
from typing import Literal, Optional
from glue.database.database import GlueGuild

# connection to database
db = Database()


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
    async def add(self, interaction: discord.Interaction, name: str, canister_id: str, standard: Literal['ext', 'dip721'], role: str):
        """Set up an NFT project"""
        try:
            if interaction.guild_id:
                document: GlueGuild = {
                    "guildId": interaction.guild_id,
                    "canisters": [
                        {
                            "canisterId": canister_id,
                            "tokenStandard": standard,
                            "role": role,
                            "name": name,
                            "users": []
                        }
                    ]

                }
                db.insert(document)
                await interaction.response.send_message(f'Added project {name} to database', ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f'Error: {e}', ephemeral=True)

    @app_commands.command()
    @app_commands.guild_only()
    @app_commands.default_permissions()
    async def list(self, interaction: discord.Interaction):
        """List all projects"""
        guild: Optional[GlueGuild] = db.find_one(
            {"guildId": interaction.guild_id})
        if not guild or not guild['canisters']:
            await interaction.response.send_message('No projects found', ephemeral=True)
        else:
            message_string = ''
            for project in guild['canisters']:
                message_string += f'📇 name: {project["name"]}\n🪪canister id: {project["canisterId"]}\n🕵🏿‍♂️ role: {project["role"]}\n💾 standard: {project["tokenStandard"]}\n\n'
            await interaction.response.send_message(message_string, ephemeral=True)

    @app_commands.command()
    @app_commands.guild_only()
    @app_commands.default_permissions()
    @app_commands.describe(
        canister_id='Please specify the canister ID of the project you want to delete, e.g. `pk6rk-6aaaa-aaaae-qaazq-cai`',
    )
    async def remove(self, interaction: discord.Interaction, canister_id: str):
        """Remove a project"""
        try:
            result = db.delete_canister(interaction.guild_id, canister_id)
            await interaction.response.send_message(f'Removed project {canister_id} from database. {result}', ephemeral=True)
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
