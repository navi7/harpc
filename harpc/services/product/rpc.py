import pymongo
from bson.json_util import dumps

from rpc.server import rpc


client = pymongo.MongoClient('storage_product')
database = client.product_db
products = database.product


@rpc
async def create(name):
    print('Creating product {}'.format(name))

    inserted = products.insert_one({'name': name})
    return dumps(products.find_one({'_id': inserted.inserted_id}))


@rpc
async def get_by_name(name):
    print("Looking up product with name {}".format(name))

    return dumps(products.find_one({'name': name}))
