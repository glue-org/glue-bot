from bson.objectid import ObjectId
from glue.database.database import (
    GlueUser,
    Database,
    GlueGuild,
    Canister as GlueCanister,
    TokenStandard,
)
from ic.client import Client
from ic.identity import Identity
from ic.agent import Agent
from ic.agent import Principal
from ic.canister import Canister
import discord
from discord.utils import get
import logging
from pathlib import Path
from typing import Optional

# create logger
logger = logging.getLogger("discord")

# create agent
iden = Identity()
client = Client()
agent = Agent(iden, client)

# create DB
db = Database()

ext_candid = open(Path(__file__).parent / ".." / "dids" / "ext.did").read()
dip721_candid = open(Path(__file__).parent / ".." / "dids" / "dip721.did").read()
ogy_candid = open(Path(__file__).parent / ".." / "dids" / "ogy.did").read()
icp_ledger_candid = open(
    Path(__file__).parent / ".." / "dids" / "icp-ledger.did"
).read()
ccc_candid = open(Path(__file__).parent / ".." / "dids" / "ccc.did").read()
icrc_1_candid = open(Path(__file__).parent / ".." / "dids" / "icrc-1.did").read()
dip20_candid = open(Path(__file__).parent / ".." / "dids" / "dip20.did").read()


async def verify_ownership_for_guild(guild: GlueGuild, bot: discord.Client):
    for canister in guild["canisters"]:
        logger.info(f"verifying ownership for canister {canister['name']}")
        for user_id in canister["users"]:
            await verify_ownership_for_user(user_id, bot, canister, guild)


async def verify_ownership_for_user(
    user_id: ObjectId, bot: discord.Client, canister: GlueCanister, guild: GlueGuild
):
    # get the user from the database
    user_from_db = db.get_user(user_id)
    try:
        if user_from_db:
            # for all the attached principals, check if the user owns the NFT
            has_token = False
            for principal in user_from_db["principals"]:
                # check if all returns in the for loop are true
                tokens = await user_has_tokens(
                    canister["tokenStandard"],
                    principal,
                    canister["canisterId"],
                    canister.get(
                        "min"
                    ),  # this will return None if the key doesn't exist
                    canister.get("max"),
                )
                if tokens:
                    has_token = True
                    break
            if not has_token:
                # remove the role from the user
                await remove_role_from_user(user_from_db, guild, canister["role"], bot)
                # remove the user from the project
                db.delete_user_from_canister(
                    guild["guildId"], canister["canisterId"], user_id
                )
    except Exception:
        logger.exception("error checking ownership")


async def user_has_tokens(
    standard: TokenStandard,
    principal: str,
    canister_id: str,
    min: Optional[int],
    max: Optional[int],
) -> bool:
    if standard == "ext":
        ext = Canister(agent=agent, canister_id=canister_id, candid=ext_candid)
        account = Principal.from_str(principal).to_account_id().to_str()[2:]
        result = await ext.tokens_async(account)  # type: ignore
        try:
            if min and max:
                if min <= len(result[0]["ok"]) <= max:
                    return True
            elif min:
                if min <= len(result[0]["ok"]):
                    return True
            elif max:
                if len(result[0]["ok"]) <= max:
                    return True
            else:
                if len(result[0]["ok"]) != 0:
                    return True
        except Exception:
            return False
    elif standard == "dip721":
        dip721 = Canister(agent=agent, canister_id=canister_id, candid=dip721_candid)
        result = await dip721.ownerTokenIdentifiers_async(principal)  # type: ignore
        try:
            if min and max:
                if min <= len(result[0]["Ok"]) <= max:
                    return True
            elif min:
                if min <= len(result[0]["Ok"]):
                    return True
            elif max:
                if len(result[0]["Ok"]) <= max:
                    return True
            else:
                if len(result[0]["Ok"]) != 0:
                    return True
        except Exception:
            return False
    elif standard == "ogy":
        ogy = Canister(agent=agent, canister_id=canister_id, candid=ogy_candid)
        result = await ogy.balance_of_nft_origyn_async(  # type: ignore
            {
                "principal": principal,
            }
        )

        try:
            if min and max:
                if min <= len(result[0]["ok"]["nfts"]) <= max:
                    return True
            elif min:
                if min <= len(result[0]["ok"]["nfts"]):
                    return True
            elif max:
                if len(result[0]["ok"]["nfts"]) <= max:
                    return True
            else:
                if len(result[0]["ok"]["nfts"]) != 0:
                    return True
        except Exception:
            return False
    elif standard == "icp-ledger":
        account = Principal.from_str(principal).to_account_id().bytes
        icp_ledger = Canister(
            agent=agent, canister_id=canister_id, candid=icp_ledger_candid
        )

        result = await icp_ledger.account_balance_async({"account": account})  # type: ignore
        try:
            if min and max:
                if min <= result[0]["e8s"] <= max:
                    return True
            elif min:
                if min <= result[0]["e8s"]:
                    return True
            elif max:
                if result[0]["e8s"] <= max:
                    return True
            else:
                if result[0]["e8s"] != 0:
                    return True
        except Exception:
            return False
    elif standard == "ccc":
        ccc = Canister(agent=agent, canister_id=canister_id, candid=ccc_candid)

        result = await ccc.balanceOf_async(principal)  # type: ignore
        try:
            if min and max:
                if min <= result[0] <= max:
                    return True
            elif min:
                if min <= result[0]:
                    return True
            elif max:
                if result[0] <= max:
                    return True
            else:
                if result[0] != 0:
                    return True
        except Exception:
            return False
    elif standard == "icrc-1":
        icrc_1 = Canister(agent=agent, canister_id=canister_id, candid=icrc_1_candid)

        result = await icrc_1.icrc1_balance_of_async(  # type: ignore
            {"owner": principal, "subaccount": []}
        )
        try:
            if min and max:
                if min <= result[0] <= max:
                    return True
            elif min:
                if min <= result[0]:
                    return True
            elif max:
                if result[0] <= max:
                    return True
            else:
                if result[0] != 0:
                    return True
        except Exception:
            return False
    elif standard == "dip20":
        dip20 = Canister(agent=agent, canister_id=canister_id, candid=dip20_candid)

        result = await dip20.balanceOf_async(principal)  # type: ignore
        try:
            if min and max:
                if min <= result[0] <= max:
                    return True
            elif min:
                if min <= result[0]:
                    return True
            elif max:
                if result[0] <= max:
                    return True
            else:
                if result[0] != 0:
                    return True
        except Exception:
            return False
    return False


async def remove_role_from_user(
    user: GlueUser, guild: GlueGuild, role: str, bot: discord.Client
):
    # move import to avoid circular dependencies
    discord_guild = bot.get_guild(int(guild["guildId"]))
    if discord_guild:
        logger.warn(
            f"removing role {role} from user {user['discordId']} in guild {discord_guild}"
        )
        # get role by name
        role_snowflake = get(discord_guild.roles, name=role)
        #  this needs the members intent to be on
        discord_user = discord_guild.get_member(int(user["discordId"]))
        if discord_user and role_snowflake:
            try:
                await discord_user.remove_roles(role_snowflake)
            except Exception:
                logger.exception(Exception)
