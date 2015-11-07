import collections
import inspect
import logging

from .queue_client import QueueClient

logging.basicConfig(level=logging.INFO)

rpc_record = collections.namedtuple('RpcRecord', ['function', 'signature'])


def rpc(function):
    """
    Decorator for methods that need to be exposed over RPC
    """
    # Register `function` as available over RPC
    record = rpc_record(function, inspect.signature(function))

    HARPCServer.register(function.__name__, record)

    return function


class HARPCServer(QueueClient):
    EXCHANGE = 'rpc'

    # registry of available procedures
    registry = {}

    def __init__(self, broker_url, service):
        super().__init__(broker_url)

        self.service = service
        self.queue_name = 'rpc.{service}'.format(service=service)
        self.routing_key = 'rpc.{service}.#'.format(service=service)

    def __enter__(self):
        self.subscribe(routing_key=self.routing_key,
                       queue_name=self.queue_name,
                       durable=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.release()

    @classmethod
    def register(cls, function_name, record):
        cls.registry[function_name] = record
        logging.info('Registered function "{}" for RPC'.format(function_name))

    def run_forever(self):
        logging.info('Running RPC server...')
        self.loop.run_forever()

    @staticmethod
    def extract_function_name(routing_key):
        # routing key is rpc.SERVICE_NAME.FUNCTION_NAME
        return routing_key.split('.')[-1]

    async def handle_call(self, payload, message):
        reply_to = message.properties.get('reply_to')
        correlation_id = message.properties.get('correlation_id')

        function_name = self.extract_function_name(message.delivery_info['routing_key'])
        try:
            record = self.registry.get(function_name)
            bound = record.signature.bind(*{}, **payload)
            logging.info('Running {}({})'.format(function_name, payload))
            response = await record.function(*{}, **bound.arguments)
        except Exception as ex:
            logging.exception('Error running RPC procedure')
            response = {'error': str(ex)}

        self.publish(routing_key=reply_to, payload=response, correlation_id=correlation_id, exchange='')

