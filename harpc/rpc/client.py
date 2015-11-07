import uuid
import asyncio
import logging

from .queue_client import QueueClient

logging.basicConfig(level=logging.INFO)


class ClientCall(object):

    def __init__(self, client, function):
        self.client = client
        self.function = function

        self.correlation_id = str(uuid.uuid4())

        self.kwargs = None

        # wait handle
        self.future = asyncio.Future()

    async def __call__(self, *args, **kwargs):
        assert len(args) == 0, "Positional arguments are not supported"
        self.kwargs = kwargs
        return await self.client.execute_call(self)


class HARPCClient(QueueClient):

    EXCHANGE = 'rpc'
    QUEUE_TYPE = 'topic'

    def __init__(self, broker_url, service_name, timeout=None):
        super().__init__(broker_url, timeout)
        self.service_name = service_name

        # we need to wait for a queue to be created
        self.queue_name_declared = asyncio.Future()
        self._queue_name = None

        # we need to remember the call so when we get a response
        # we can match it and return it to the caller
        self.call_registry = {}

    def _on_declared(self, queue_name, _, __):
        # the queue was created, remember it's name
        self.queue_name_declared.set_result(queue_name)

    async def get_queue_name(self):
        if self._queue_name is None:
            await self.queue_name_declared
            self._queue_name = self.queue_name_declared.result()

        return self._queue_name

    def __getattr__(self, name):
        # any attribute is considered a function_name
        return ClientCall(client=self, function=name)

    async def execute_call(self, client_call):
        # remember what we sent
        self.call_registry[client_call.correlation_id] = client_call

        self.subscribe_exclusive(auto_delete=True,
                                 on_declared=self._on_declared)

        self.queue_name = await self.get_queue_name()
        routing_key = 'rpc.{}.{}'.format(self.service_name,
                                         client_call.function)

        logging.info('Calling {}({})'.format(routing_key, client_call.kwargs))
        self.publish(routing_key=routing_key,
                     payload=client_call.kwargs,
                     correlation_id=client_call.correlation_id,
                     reply_to=self.queue_name)

        self.loop.call_soon(self.drain_events)
        if not self.loop.is_running():
            self.loop.call_soon(self.loop.run_until_complete(client_call.future))
        try:
            logging.info('Waiting for response from server')
            await asyncio.wait_for(asyncio.shield(client_call.future), self.timeout)
            return client_call.future.result()
        except asyncio.TimeoutError:
            raise Exception('Timeout!')

    async def handle_call(self, payload, message):
        logging.info('Got response from server: {}, {}'.format(payload, message))
        correlation_id = message.properties.get('correlation_id')
        client_call = self.call_registry.pop(correlation_id)

        if isinstance(payload, dict) and 'error' in payload:
            client_call.future.set_exception(Exception(payload['error']))
        else:
            client_call.future.set_result(payload)
