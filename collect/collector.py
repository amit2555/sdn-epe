#!/usr/bin/env python

from automation import tasks
from utilities.settings import DEVICES
from utilities.utils import db_connect
from kafka import KafkaProducer
import time
import json


def write_to_database(collection, device, data):
    with db_connect("sdn") as db:
        for row in data:
            row["device"] = device
            db[collection].insert(row)


"""
def main():

    while True:
        for device in DEVICES:
            mpls = tasks.get_mpls_table(device)
            write_to_database("mpls", device, mpls)
            utilization = tasks.get_interfaces_utilization(device)
            write_to_database("interface", device, utilization)

        time.sleep(60)
"""

def main():

    producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
    while True:
        for device in ["2.2.2.2"]:
            utilization = json.dumps(tasks.get_interfaces_utilization(device))
            producer.send(device, key=json.dumps({"type":"utilization", "device":device}), value=utilization)
            print "Message sent..."
        time.sleep(60)


if __name__ == "__main__":
    main()

