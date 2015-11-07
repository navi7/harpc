import os

import pymongo
from bson.json_util import dumps, loads

from rpc.server import rpc
from rpc.client import HARPCClient

broker_url = os.environ.get('RPC_QUEUE', 'amqp://guest:guest@localhost:5672/')
product_service = 'product'
account_service = 'account'

client = pymongo.MongoClient('storage_warehouse')
database = client.warehouse_db
warehouses = database.warehouse
inventories = database.inventory
sells = database.sell


@rpc
async def create(name):
    print("Creating a warehouse with name {}".format(name))

    inserted = warehouses.insert_one({'name': name})
    return dumps(warehouses.find_one({'_id': inserted.inserted_id}))


@rpc
async def intake(warehouse, product, quantity):
    print("Intaking product {} into warehouse {}. Quantity: {}".format(
        product, warehouse, quantity
    ))

    warehouse_data = warehouses.find_one({'name': warehouse})
    if warehouse_data is None:
        return {'error': 'No warehouse with name {}'.format(warehouse)}

    product_client = HARPCClient(broker_url=broker_url,
                                 service_name=product_service,
                                 timeout=5)

    product_data = loads(await product_client.get_by_name(name=product))

    intake_data = {
        'warehouse_id': warehouse_data['_id'],
        'product_id': product_data['_id']
    }

    result = inventories.find_one(intake_data)
    if result is None:
        print('Inserting new intake')
        intake_data['quantity'] = quantity
        inserted = inventories.insert_one(intake_data)
        return dumps(inserted.inserted_id)
    else:
        print('Updating existing intake')
        quantity += result['quantity']
        inventories.update_one(
            {'_id': result['_id']},
            {'$set': {'quantity': quantity}}
        )
        return dumps(result['_id'])


@rpc
async def ship_to(warehouse, buyer, product, quantity):
    print("Sold product {} to buyer {} from warehouse {}. Quantity: {}".format(
        product, buyer, warehouse, quantity
    ))

    warehouse_data = warehouses.find_one({'name': warehouse})
    if warehouse_data is None:
        return {'error': 'No warehouse with name {}'.format(warehouse)}

    product_client = HARPCClient(broker_url=broker_url,
                                 service_name=product_service,
                                 timeout=5)

    product_data = loads(await product_client.get_by_name(name=product))

    inventory_data = {
        'warehouse_id': warehouse_data['_id'],
        'product_id': product_data['_id']
    }
    result = inventories.find_one(inventory_data)
    if result is None:
        return {'error': 'No product {} in warehouse {}'.format(product, warehouse)}

    if result['quantity'] < quantity:
        return {
            'error': 'Not enough of product {} in warehouse {}. We only have {}'.format(
                product, warehouse, quantity)
        }

    account_client = HARPCClient(broker_url=broker_url,
                                 service_name=account_service,
                                 timeout=5)

    buyer_data = loads(await account_client.get_by_name(name=buyer))

    sell_data = {
        'buyer_id': buyer_data['_id'],
        'product_id': product_data['_id'],
        'quantity': quantity
    }

    quantity = result['quantity'] - quantity
    inventories.update_one(
        {'_id': result['_id']},
        {'$set': {'quantity': quantity}}
    )

    inserted = sells.insert_one(sell_data)
    return dumps(inserted.inserted_id)

