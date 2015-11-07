import pymongo
from bson.json_util import dumps

from rpc.server import rpc


client = pymongo.MongoClient('storage_account')
database = client.account_db
accounts = database.account


@rpc
async def create(name, account_type):
    print("Creating account with name {} and type {}".format(name, account_type))

    inserted = accounts.insert_one({'name': name, 'account_type': account_type})
    return dumps(accounts.find_one({'_id': inserted.inserted_id}))


@rpc
async def get_by_name(name):
    print("Looking up account with name {}".format(name))

    return dumps(accounts.find_one({'name': name}))
