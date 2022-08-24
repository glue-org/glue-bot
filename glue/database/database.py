from bson.objectid import ObjectId
from pymongo.mongo_client import MongoClient
from typing import Optional, TypedDict, Literal
import urllib.parse
import os
from dotenv import load_dotenv

load_dotenv()
MONGO_USERNAME = os.getenv('MONGO_USERNAME')
MONGO_PW = os.getenv('MONGO_PW')


class Canister(TypedDict):
    canisterId: str
    tokenStandard: Literal['ext', 'dip721', 'ogy', 'icp-ledger', 'ccc', 'icrc-1']
    role: str
    name: str
    users: list[ObjectId]


class GlueGuild(TypedDict):
    guildId: str
    canisters: list[Canister]


class GlueUser(TypedDict):
    discordId: str
    principals: list[str]


class Guilds:
    def __init__(self):
        try:
            # connect to local mongoDB using username and password of admin user
            if MONGO_USERNAME is not None and MONGO_PW is not None:
                self.client = MongoClient(
                    f"mongodb://{urllib.parse.quote_plus(MONGO_USERNAME)}:{urllib.parse.quote_plus(MONGO_PW)}@127.0.0.1:27017/")
            else:
                self.client = MongoClient()
        except Exception as e:
            print("database connection error")
            raise e
        self.db = self.client.glue_discord
        self.collection = self.db.guilds

    def create_guild(self, guild_id: str, canister_id: str, token_standard: Literal['ext', 'dip721', 'ogy', 'icp-ledger', 'ccc', 'icrc-1'], role: str, name: str):
        # if the document already exists, update it
        if self.collection.find_one({"guildId": guild_id}):
            # make sure the canisters are unique
            if not self.collection.find_one({"guildId": guild_id, "canisters.canisterId": canister_id}):
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

    def get_guilds(self):
        return self.collection.find()

    def get_guild_by_id(self, guild_id: str):
        return self.collection.find_one({"guildId": guild_id})

    def delete_user_from_canister(self, guild_id: str, canister_id: str, user_id: ObjectId):
        self.collection.find_one_and_update(
            {"guildId": guild_id, "canisters.canisterId": canister_id},
            {"$pull": {"canisters.$.users": user_id}}
        )

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


class Users:
    def __init__(self):
        try:
            # connect to local mongoDB using username and password of admin user
            if MONGO_USERNAME is not None and MONGO_PW is not None:
                self.client = MongoClient(
                    f"mongodb://{urllib.parse.quote_plus(MONGO_USERNAME)}:{urllib.parse.quote_plus(MONGO_PW)}@127.0.0.1:27017/")
            else:
                self.client = MongoClient()
        except Exception as e:
            print("database connection error")
            raise e
        self.db = self.client.glue_discord
        self.collection = self.db.users

    def get_user(self, user_id: ObjectId) -> Optional[GlueUser]:
        return self.collection.find_one({"_id": user_id})
