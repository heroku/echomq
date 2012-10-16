echmq
-----

Generic echo server. Consumes messages from a broker and writes to socket.io, database, etc.

Usage: ::

    $ python -m echomq --broker-url=amqp://localhost --exchange=media --queue=video --routing-key=video

