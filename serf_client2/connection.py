# -*- encoding: UTF-8 -*-

import socket
import msgpack
import resource


class ConnectionError(Exception):
    pass


class ConnectionTimeoutError(ConnectionError):
    pass



class Connection(object):
    host = None
    port = None
    timeout = None
    _socket = None
    page_size = None

    def __init__(self, host, port, timeout):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.page_size = resource.getpagesize()
        self.unpacker = msgpack.Unpacker(object_hook=_decode_addr_key)


    @property
    def socket(self):
        if not self._socket:
            try:
                self._socket = socket.create_connection((self.host, self.port), self.timeout)
            except socket.error, e:
                raise ConnectionError(*e.args)

        return self._socket


    def read(self):
        try:
            buf = self.socket.recv(self.page_size)
            if len(buf) == 0:  # Connection was closed.
                raise ConnectionError("Connection closed by peer")
            self.unpacker.feed(buf)
        except socket.timeout, e:
            raise ConnectionTimeoutError(*e.args)

        return list(self.unpacker)


    def write(self, message_or_messages):
        if isinstance(message_or_messages, list):
            to_send = ''.join((msgpack.packb(m) for m in message_or_messages))
        else:
            to_send = msgpack.packb(message_or_messages)

        self.socket.sendall(to_send)

    def close(self):
        """
        Close the connection with the Serf agent.
        """
        if self._socket:
            self._socket.close()
            self._socket = None



def _decode_addr_key(obj_dict):
    """
    Callback function to handle the decoding of the 'Addr' field.

    Serf msgpack 'Addr' as an IPv6 address, and the data needs to be unpack
    using socket.inet_ntop().

    See: https://github.com/KushalP/serfclient-py/issues/20

    :param obj_dict: A dictionary containing the msgpack map.
    :return: A dictionary with the correct 'Addr' format.
    """
    key = b'Addr'
    if key in obj_dict:
        try:
            # Try to convert a packed IPv6 address.
            # Note: Call raises ValueError if address is actually IPv4.
            ip_addr = socket.inet_ntop(socket.AF_INET6, obj_dict[key])

            # Check if the address is an IPv4 mapped IPv6 address:
            # ie. ::ffff:xxx.xxx.xxx.xxx
            if ip_addr.startswith('::ffff:'):
                ip_addr = ip_addr.lstrip('::ffff:')

            obj_dict[key] = ip_addr.encode('utf-8')
        except ValueError:
            # Try to convert a packed IPv4 address.
            ip_addr = socket.inet_ntop(socket.AF_INET, obj_dict[key])
            obj_dict[key] = ip_addr.encode('utf-8')

    return obj_dict

