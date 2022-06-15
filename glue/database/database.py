from pymongo.mongo_client import MongoClient
from typing import TypedDict, Literal


class Canister(TypedDict):
    canisterId: str
    tokenStandard: Literal['ext', 'dip721']
    role: str
    name: str
    users: list[str]


class GlueGuild(TypedDict):
    guildId: str
    canisters: list[Canister]


class Database:
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.glue_discord
        self.collection = self.db.guilds

    def insert(self, document: GlueGuild):
        # if the document already exists, update it
        if self.collection.find_one({"guildId": document['guildId']}):
            # make sure the canisters are unique
            if not self.collection.find_one({"canisters.canisterId": document['canisters'][0]['canisterId']}):
                self.collection.update_one(
                    {"guildId": document['guildId']},
                    {"$push":
                        # we have to use the first element of the list, otherwise we have nested lists
                        {"canisters": document['canisters'][0]}
                     })
        else:
            self.collection.insert_one(document)   # type: ignore

    def create_guild(self, guild_id: str, canister_id: str, token_standard: Literal['ext', 'dip721'], role: str, name: str):
        # if the document already exists, update it
        if self.collection.find_one({"guildId": guild_id}):
            # make sure the canisters are unique
            if not self.collection.find_one({"canisters.canisterId": canister_id}):
                # if they are not, update the canister
                self.collection.update_one(
                    {"guildId": guild_id},
                    {
                        "$push":
                        # we have to use the first element of the list, otherwise we have nested lists
                        {
                            "canisters":
                                {
                                    "canisterId": canister_id,
                                    "tokenStandard": token_standard,
                                    "role": role,
                                    "name": name,
                                    "users": []
                                }
                        }
                    })
            else:
                raise Exception("Canister already exists")
        else:
            self.collection.insert_one(
                {
                    "guildId": guild_id,
                    "canisters": [
                        {
                            "canisterId": canister_id,
                            "tokenStandard": token_standard,
                            "role": role,
                            "name": name,
                            "users": []
                        }
                    ]
                }
            )

    def find(self, query):
        return self.collection.find(query)

    def get_guild_by_id(self, guild_id: str):
        return self.collection.find_one({"guildId": guild_id})

    def update(self, query, update):
        self.collection.update_one(query, update)

    def delete_server(self, query):
        return self.collection.delete_one(query)

    def delete_canister(self, guild_id: str, canister_id: str):
        # if the document already exists, update it
        if not self.collection.find_one({"guildId": guild_id, "canisters.canisterId": canister_id}):
            raise Exception("Canister does not exist")
        else:
            self.collection.update_one(
                {"guildId": guild_id},
                {
                    "$pull":
                        {
                            "canisters":
                                {
                                    "canisterId": canister_id
                                }
                        }
                })
