#!/usr/bin/env python

from automation.auto_operations.helpers import interface_expand
from collections import defaultdict
from pprint import pprint as pp
import time
import json
import zmq


def bind_to_socket(port):
    """Bind to a socket on a unique port."""

    c = zmq.Context()
    s = c.socket(zmq.SUB)
    s.bind('tcp://127.0.0.1:' + str(port))
    s.setsockopt(zmq.SUBSCRIBE, '')
    return s


def main():

    repository = defaultdict(dict)
    nlri = 'ipv4 nlri-mpls'

    # Socket used to collect data from Collector
    collector = bind_to_socket(5001)
    # Socket used to collect BGP Updates from Exabgp
    update_puller = bind_to_socket(6000)

    while True:
        if collector.poll(100):
            msg = collector.recv_json()
            asbr_name = msg['name']

            if msg['type'] == 'mpls':
                for elem in msg['data']:
                    if elem['prefix'] in repository[asbr_name]:
                        repository[asbr_name][elem['prefix']].update(
                                             {'interface':interface_expand(elem['interface'])})

            if msg['type'] == 'util':
                for elem in msg['data']:
                    for prefix in repository[asbr_name]:
                        if elem['name'] == repository[asbr_name][prefix]['interface']:
                            repository[asbr_name][prefix].update(
                                                      {'input_util':elem['input_util'],
                                                       'output_util':elem['output_util']})
            pp(repository)


        if update_puller.poll(100):
            msg = update_puller.recv_json()
            #print msg
            asbr_name = msg['ip']
            bgp_update = msg['message']['update']

            if 'announce' in bgp_update:
                for nexthop in bgp_update['announce'][nlri]:
                    for prefix in bgp_update['announce'][nlri][nexthop]:
                        repository[asbr_name][prefix] = bgp_update['announce'][nlri][nexthop][prefix]
                        repository[asbr_name][prefix].update({'nexthop':nexthop, 'attributes':bgp_update['attribute']})
                                                     
            if 'withdraw' in bgp_update:
                for prefix in bgp_update['withdraw'][nlri]:
                    repository[asbr_name].pop(prefix) 


 

if __name__ == "__main__":
    main()

 
