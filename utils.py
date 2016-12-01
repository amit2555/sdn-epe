#!/usr/bin/env python

import zmq


def sub_connect(port):
    """Subscriber: Connect to a socket on a unique port."""

    c = zmq.Context()
    s = c.socket(zmq.SUB)
    s.connect('tcp://127.0.0.1:' + str(port))
    s.setsockopt(zmq.SUBSCRIBE, '')
    return s

def pub_bind(port):
    """Publisher: Bind to a socket on a unique port."""

    c = zmq.Context()
    s = c.socket(zmq.PUB)
    s.bind('tcp://127.0.0.1:' + str(port))
    return s

def sub_bind(port):
    """Subscriber: Bind to a socket on a unique port."""

    c = zmq.Context()
    s = c.socket(zmq.SUB)
    s.bind('tcp://127.0.0.1:' + str(port))
    s.setsockopt(zmq.SUBSCRIBE, '')
    return s

