import os
import sys
import json
import argparse
import asyncio

from rpc.client import HARPCClient

broker_url = os.environ.get('RPC_QUEUE', 'amqp://guest:guest@localhost:5672/')


async def execute(service_name, procedure_name, timeout):
    client = HARPCClient(broker_url=broker_url, service_name=service_name, timeout=timeout)
    procedure = getattr(client, procedure_name)
    if procedure:
        print('Provide data for function and finish with Ctrl+D: ')
        data = json.loads(sys.stdin.read() or '{}')

        print('Calling {}.{}({})'.format(service_name, procedure_name, data))
        try:
            response = await procedure(**data)
            print('-'*60)
            print(response)
        except Exception as ex:
            print('Error: {}'.format(ex))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Call RPC service endpoints')
    parser.add_argument('service', help='Name of the service to call')
    parser.add_argument('procedure', help='Name of the procedure to call')

    parser.add_argument('-t', '--timeout', help='How long to wait for server to respond',
                        type=int, default=10)

    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        execute(args.service, args.procedure, args.timeout)
    )
