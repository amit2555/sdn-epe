#!/usr/bin/env python

import json
import sys
import select
import logging
from utilities.settings import CONFIG
from controller import Router


logger = logging.getLogger("__name__")
logging.basicConfig(level=logging.DEBUG)

instances = dict()
inputs = [sys.stdin]
NLRI = CONFIG["NLRI"]

while True:
    bgp_update = None
    message_received = False

    read_ready, write_ready, except_ready = select.select(inputs, [], [], 0.1)

    for readable in read_ready:
        if readable is sys.stdin:
            line = sys.stdin.readline().strip()
            message = json.loads(line)
            message_received = True

    if message_received and message["type"] == "update":
        bgp_update = message["neighbor"]["message"]["update"]
        asbr_name = message["neighbor"]["address"]["peer"]
      
        # Accept only BGP Labeled-Unicast updates
        if "announce" in bgp_update and NLRI in bgp_update["announce"]:
            instances[asbr_name].prefix_announced(bgp_update)
  
        if "withdraw" in bgp_update and NLRI in bgp_update["withdraw"]:
            instances[asbr_name].prefix_withdrawn(bgp_update)

    # Monitor BGP neighbor changes and remove peer if Down
    if message_received and message["type"] == "state":
        status = message["neighbor"]["state"]
        asbr_name = message["neighbor"]["address"]["peer"]
        if not instances.get(asbr_name):
            instances[asbr_name] = Router(asbr_name)

        instances[asbr_name].update_status(status)


