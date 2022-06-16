from glue.database.database import Users, GlueGuild
from ic.client import Client
from ic.identity import Identity
from ic.agent import Agent
from ic.agent import Principal
from ic.candid import Types, encode
from ic.canister import Canister

# create agent
iden = Identity()
client = Client()
agent = Agent(iden, client)

# create DB
db = Users()

ext_candid = open('ext.did').read()
dip721_candid = open('dip721.did').read()


def verify_ownership_for_guild(guild: GlueGuild):
    for canister in guild['canisters']:
        for user_id in canister['users']:
            # get the user from the database
            user_from_db = db.get_user(user_id)
            if user_from_db:
                # for all the attached principals, check if the user owns the NFT
                for principal in user_from_db['principals']:
                    user_has_tokens(
                        canister['tokenStandard'], principal, canister['canisterId'])


def user_has_tokens(standard: str, principal: str, canister_id: str) -> bool:
    if standard == 'ext':
        ext = Canister(agent=agent, canister_id=canister_id,
                       candid=ext_candid)
        account = Principal.from_str(principal).to_account_id().to_str()[:2]
        result = ext.tokens(account)  # type: ignore
        try:
            result[0]['ok']  # type: ignore
            return True
        except KeyError:
            return False
    else:
        dip721 = Canister(agent=agent, canister_id=canister_id,
                          candid=dip721_candid)
        result = dip721.ownerTokenIdentifiers(principal)   # type: ignore
        try:
            result[0]['Ok']  # type: ignore
            return True
        except KeyError:
            return False
