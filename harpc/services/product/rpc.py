import uuid

from rpc.server import rpc


@rpc
async def create(name):
    print('Creating product {}'.format(name))

    return {'uuid': str(uuid.uuid4()), 'name': name}
