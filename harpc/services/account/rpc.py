import uuid

from rpc.server import rpc


@rpc
def create(name, account_type):
    print("Creating account with name {} and type {}".format(name, account_type))

    return {'uuid': str(uuid.uuid4()), 'name': name, 'account_type': account_type}
