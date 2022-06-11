from pymongo.mongo_client import MongoClient
from typing import TypedDict, Literal


class Canister(TypedDict):
    canisterId: str
    tokenStandard: Literal['ext', 'dip721']
    role: str
    name: str
    users: list[str]


class GlueGuild(TypedDict):
    guildId: int
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

    def find(self, query):
        return self.collection.find(query)

    def find_one(self, query):
        return self.collection.find_one(query)

    def update(self, query, update):
        self.collection.update_one(query, update)

    def delete_server(self, query):
        return self.collection.delete_one(query)

    def delete_canister(self, guild_id, canister_id):
        return self.collection.update_one(
            {"server_id": guild_id},
            {"$pull":
             {"canisters":
              {"canister_id": canister_id}
              }
             })
