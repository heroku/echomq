import sys

from kombu import Connection, Exchange, Queue


def main():
    n = int(sys.argv[1]) if len(sys.argv)>1 else 10

    exchange = Exchange('test', 'direct', durable=True)
    queue = Queue('test', exchange=exchange, routing_key='test')

    with Connection('amqp://localhost') as conn:
        with conn.Producer(serializer='json') as producer:
            for i in range(n):
                producer.publish(
                        {'n': i},
                        exchange=exchange, routing_key='test',
                        declare=[queue])


if __name__ == '__main__':
    main()
