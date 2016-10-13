#!/usr/bin/python

from collections import defaultdict
from sys import stdin
from automation import tasks
import time
import json

'''
def map_label_to_interface(peer):
    return mappings
'''


received_prefixes = defaultdict(dict)
nlri = 'ipv4 nlri-mpls'

while True:
    line = stdin.readline().strip()
    bgp_update = json.loads(line)

    #json.dump(bgp_update, open('/tmp/text.txt','a')) 

    update_data = False
    if bgp_update['type'] == 'update':
        peer = bgp_update['neighbor']['address']['peer']
        update = bgp_update['neighbor']['message']['update']
      
        # Ignore IPv4-Unicast updates 
        if 'announce' in update and 'ipv4 unicast' in update['announce']:
            continue 
        if 'withdraw' in update and 'ipv4 unicast' in update['withdraw']:
            continue

        # Accept Labeled-Unicast updates
        if 'announce' in update and nlri in update['announce']:
            received_prefixes[peer].update(update['announce'][nlri][peer])
            update_data = True
        if 'withdraw' in update and nlri in update['withdraw']:
            for prefix in update['withdraw'][nlri].keys():
                received_prefixes[peer].pop(prefix) 
            update_data = True

        # Code to map label-to-interface

    if update_data:        
        for egress_router, prefixes in received_prefixes.iteritems():
            mpls_table = tasks.get_mpls_table(egress_router)
            for elem in mpls_table:
                for prefix, label in prefixes.iteritems(): 
                    if prefix == elem['prefix'] and label['label'][0] == int(elem['local_label']):
                        received_prefixes[egress_router][prefix].update({'interface': elem['interface']})
        
    json.dump(received_prefixes, open('/tmp/text.txt','w')) 
