import uuid

from rpc.server import rpc


@rpc
def create(name):
    print("Creating a warehouse with name {} and type {}".format(name))

    return {'uuid': str(uuid.uuid4()), 'name': name}
