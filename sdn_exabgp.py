#!/usr/bin/env python

import json
import zmq
import sys
import select
from collections import defaultdict
from utilities.utils import pub_bind


asbr_info = defaultdict(dict)
nlri = 'ipv4 nlri-mpls'
device_producer = pub_bind(5000) 
update_producer = pub_bind(6000) 
inputs = [sys.stdin]

while True:
    bgp_update = None
    prefix_updated = prefix_withdrawn = message_received = False

    read_ready, write_ready, except_ready = select.select(inputs, [], [], 0.1)

    for readable in read_ready:
        if readable is sys.stdin:
            line = sys.stdin.readline().strip()
            message = json.loads(line)
            message_received = True

    if message_received and message['type'] == 'update':
        bgp_update = message['neighbor']['message']['update']
      
        # Publish only Labeled-Unicast updates
        if 'announce' in bgp_update and nlri in bgp_update['announce']:
            prefix_updated = True
        if 'withdraw' in bgp_update and nlri in bgp_update['withdraw']:
            prefix_withdrawn = True

    # Send BGP Update message over 0mq
    if prefix_updated or prefix_withdrawn:
        update_producer.send_json(message['neighbor'])

    # Monitor BGP neighbor changes and remove peer if Down
    if message_received and message['type'] == 'state':
        state = message['neighbor']['state']
        asbr = message['neighbor']['address']['peer']

        if state == 'down':
            asbr_info[asbr].update({'name':asbr, 'status':'down'})

        if state == 'up':
            asbr_info[asbr].update({'name':asbr, 'status':'up'})

        if state == 'up' or state == 'down':
            device_producer.send_json(asbr_info[asbr])


    '''
    if prefix_withdrawn or state_changed:
        ## Code to check if any Ingress routers were programmed through Controller
        ## If so, withdraw advertisement if prefix was withdrawn by egress router.
        pass

    counter += 1
    if counter != 300:
        time.sleep(1)
    else:
        # Connect to elasticsearch and find top-talkers in last 5 mins.
        pass
    '''
