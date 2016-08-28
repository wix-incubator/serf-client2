# -*- encoding: UTF-8 -*-
from time import sleep
from connection import Connection, ConnectionError, ConnectionTimeoutError


class Result(object):
    head = None
    body = None

    def __init__(self, messages=None):
        if messages is not None:
            self.head = messages[0]
            if len(messages) > 1:
                self.body = messages[1]


class Client(object):
    host = None
    port = None
    timeout = None
    retrys = None
    retry_timeout = None

    _seq = None
    _connection = None
    key = None

    def __init__(self, host='127.0.0.1', port=7373, timeout=3, retrys=10, retry_timeout=5, auth_key=None):
        self.host = host
        self.port = port
        self.timeout = timeout
        self._connection = None
        self._seq = 0

        self.retrys = retrys
        self.retry_timeout = retry_timeout
        self.key = auth_key

    @property
    def connection(self):
        # if not self._connection:
        #     self._connection = Connection(host=self.host, port=self.port, timeout=self.timeout)

        attempt = 0
        while not self._connection:
            try:
                self._connection = Connection(host=self.host, port=self.port, timeout=self.timeout)
                self.handshake()
                if self.key:
                    self.auth(self.key)

            except ConnectionError, e:
                self._connection = None

                if attempt < self.retrys:
                    sleep(self.retry_timeout)
                else:
                    raise e

            attempt += 1

        return self._connection


    def close(self):
        if self._connection:
            self._connection.close()
            self._connection = None
            self._seq = 0


    def call(self, command, params=None):
        head = {'Seq': self._seq, 'Command': command}
        self._seq += 1

        if params is not None:
            self.connection.write([head, params])
        else:
            self.connection.write(head)

        return Result(self.connection.read())



    def handshake(self):
        return self.call('handshake', {"Version": 1})

    def auth(self, key):
        return self.call('auth', {"AuthKey": key})

    def install_key(self, key):
        return self.call('install-key', {"Key": key})

    def use_key(self, key):
        return self.call('use-key', {"Key": key})

    def remove_key(self, key):
        return self.call('remove-key', {"Key": key})

    def list_keys(self):
        return self.call('list-keys')

    def event(self, name, payload=None, coalesce=True):
        return self.call('event', {'Name': name, 'Payload': payload, 'Coalesce': coalesce})

    def stats(self):
        return self.call('stats')

    def join(self, location):
        if not isinstance(location, (list, tuple)):
            location = (location,)
        return self.call('join', {"Existing": location, "Replay": False})

    def force_leave(self, node_name):
        """
        Removes a failed node from the cluster
        :param node_name:
        """
        return self.call('force-leave', {"Node": node_name})

    def get_coordinate(self, node_name):
        """
        The get-coordinate command is used to obtain the network coordinate of a given node.
        :param node_name:
        """
        return self.call('get-coordinate', {"Node": node_name})

    def leave(self):
        """
        The leave command is used trigger a graceful leave and shutdown.
        """
        return self.call('leave')


    def members(self):
        return self.call('members')

    def members_filtered(self, tags=None, status=None, name=None):
        params = {}

        if tags is not None:
            params['Tags'] = tags

        if status is not None:
            params['Status'] = status

        if name is not None:
            params['Name'] = name

        return self.call('members-filtered', params)

    def tags(self, add_tags=None, delete_tags=None):
        return self.call('tags', {'Tags': add_tags, 'DeleteTags': delete_tags})


    def _subscribe(self, subscribe_command, callback=None, args=None, kwargs=None):
        if args is None:
            args = ()

        if kwargs is None:
            kwargs = {}

        if not hasattr(callback, '__call__'):
            raise TypeError('callback must be a function')

        res = self.call(*subscribe_command)
        sec = res.head.get('Seq')

        stop_reading = False
        while not stop_reading:
            try:
                res = Result(self.connection.read())
                sec = res.head.get('Seq')
                stop_reading = callback(res, *args, **kwargs)
            except ConnectionTimeoutError:
                stop_reading = callback(None, *args, **kwargs)

        self.call('stop', {"Stop": sec})

    def stream(self, event_type='*', callback=None, args=None, kwargs=None):
        self._subscribe(('stream', {"Type": event_type}), callback, args, kwargs)

    def monitor(self, log_level='DEBUG', callback=None, args=None, kwargs=None):
        self._subscribe(('monitor', {"LogLevel": log_level}), callback, args, kwargs)




# TODO:
# query - Initiates a new query
# respond - Responds to an incoming query

