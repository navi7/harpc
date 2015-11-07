import asyncio
import logging
import socket

import kombu
import kombu.pools

logging.basicConfig(level=logging.INFO)


class QueueClient(object):

    EXCHANGE = ''
    QUEUE_TYPE = 'topic'

    def __init__(self, broker_url, timeout=None):
        self.queue_name = ''
        self.broker_url = broker_url
        self.timeout = timeout

        self.loop = asyncio.get_event_loop()
        self.exchange = kombu.Exchange(self.EXCHANGE,
                                       type=self.QUEUE_TYPE,
                                       durable=True)

        self.connection = kombu.Connection(self.broker_url)
        if not self.broker_url.startswith('memory:'):
            self.connection.register_with_event_loop(self.loop)

        logging.info(
            'Connected to exchange "{}", type "{}", broker "{}"'.format(
                self.EXCHANGE, self.QUEUE_TYPE, self.broker_url
            )
        )

    async def handle_call(self, payload, message):
        raise NotImplementedError('Implement in derived class to handle received queue message')

    def handle_message(self, payload, message):
        logging.debug('hanlde_message({}, {})'.format(payload, message.properties))
        self.loop.create_task(self.handle_call(payload, message))

    def _do_subscribe(self, queue_args, **kwargs):
        queue_args.update(kwargs)

        queue = kombu.Queue(**queue_args)
        consumer = self.connection.Consumer(queue, no_ack=True)
        consumer.register_callback(self.handle_message)
        consumer.consume()

        logging.info('Subscribed to queue {} with arguments: {}'.format(self.queue_name, queue_args))
        return consumer

    def subscribe(self, routing_key, queue_name, **kwargs):
        queue_args = {
            'exchange': self.exchange,
            'name': queue_name,
            'routing_key': routing_key,
        }

        return self._do_subscribe(queue_args, **kwargs)

    def subscribe_exclusive(self, **kwargs):
        queue_args = {
            'exchange': self.exchange,
            'exclusive': True
        }

        return self._do_subscribe(queue_args, **kwargs)

    # PUBLISHING
    def publish(self, routing_key, payload, exchange=None, correlation_id=None, reply_to=None):
        producer = kombu.pools.producers[self.connection]

        declare = []
        if exchange is None:
            exchange = self.exchange
            declare += [exchange]

        with producer.acquire(block=True, timeout=60) as acquired:
            acquired.publish(payload, exchange=exchange, routing_key=routing_key, correlation_id=correlation_id,
                             reply_to=reply_to, declare=declare)

    def drain_events(self):
        if self.connection is not None:
            drain_timeout = self.timeout
            if drain_timeout is None:
                drain_timeout = 1
            try:
                self.connection.drain_events(timeout=drain_timeout)
            except socket.timeout:
                pass
