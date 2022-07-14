from glue.database.database import GlueUser, Users, GlueGuild
from ic.client import Client
from ic.identity import Identity
from ic.agent import Agent
from ic.agent import Principal
from discord.ext import commands
from ic.canister import Canister
from ic.candid import encode, Types
from discord.utils import get

# create agent
iden = Identity()
client = Client()
agent = Agent(iden, client)

# create DB
db = Users()

ext_candid = open('ext.did').read()
dip721_candid = open('dip721.did').read()
ogy_candid = open('ogy.did').read()


async def verify_ownership_for_guild(guild: GlueGuild, bot: commands.Bot):
    for canister in guild['canisters']:
        for user_id in canister['users']:
            # get the user from the database
            user_from_db = db.get_user(user_id)
            if user_from_db:
                # for all the attached principals, check if the user owns the NFT
                has_token = False
                for principal in user_from_db['principals']:
                    # check if all returns in the for loop are true
                    if user_has_tokens(
                            canister['tokenStandard'], principal, canister['canisterId']):
                        has_token = True
                        break
                if not has_token:
                    # remove the role from the user
                    await remove_role_from_user(
                        user_from_db, guild, canister['role'], bot)


def user_has_tokens(standard: str, principal: str, canister_id: str) -> bool:
    if standard == 'ext':
        ext = Canister(agent=agent, canister_id=canister_id,
                       candid=ext_candid)
        account = Principal.from_str(principal).to_account_id().to_str()[:2]
        result = ext.tokens(account)  # type: ignore
        try:
            if len(result[0]['ok']) != 0:  # type: ignore
                return True
        except Exception:
            return False
    elif standard == 'dip721':
        dip721 = Canister(agent=agent, canister_id=canister_id,
                          candid=dip721_candid)
        result = dip721.ownerTokenIdentifiers(principal)  # type: ignore
        try:
            if len(result[0]['Ok']) != 0:  # type: ignore
                return True
        except Exception:
            return False
    elif standard == 'ogy':
        types = Types.Variant({'principal': Types.Principal})  # type: ignore
        val = {'principal': principal}

        params = [
            {
                'type': types,
                'value': val
            },
        ]

        result = agent.query_raw(
            canister_id, "balance_of_nft_origyn", encode(params))

        # ogy = Canister(agent=agent, canister_id=canister_id,
        #                candid=ogy_candid)
        # result = ogy.balance_of_nft_origyn({   # type: ignore
        #     'principal': principal,
        # })

        try:
            if len(result[0]['ok']['_1224950711']) != 0:  # type: ignore
                return True
        except Exception:
            return False
    return False


async def remove_role_from_user(user: GlueUser, guild: GlueGuild, role: str, bot: commands.Bot):
    # move import to avoid circular dependencies
    discord_guild = bot.get_guild(
        int(guild['guildId']))
    if discord_guild:
        # get role by name
        role_snowflake = get(discord_guild.roles, name=role)
        discord_user = discord_guild.get_member(int(user['discordId']))
        if discord_user and role_snowflake:
            await discord_user.remove_roles(role_snowflake)
