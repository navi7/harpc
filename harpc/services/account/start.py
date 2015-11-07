import os

from rpc.server import HARPCServer

from . import rpc  # import to register procedures for RPC

broker_url = os.environ.get('RPC_QUEUE', 'memory:///')
service = 'account'


def run():
    with HARPCServer(broker_url=broker_url, service=service) as server:
        print('Running RPC server for {}'.format(service))
        server.run_forever()
