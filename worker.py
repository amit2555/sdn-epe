#!/usr/bin/env python

from utils import sub_connect
from bson.objectid import ObjecId
from pymongo import MongoClient
import datetime
import time
import logging


logger = logging.getLogger('worker')
logging.basicConfig(level=logging.DEBUG)

def get_db_connection(db_name):
    conn = MongoClient("mongodb://localhost:27017")
    db = conn[db_name]
    

def main():

    """
    instances = dict()
    controller = sub_connect(5002)

    while True:

        if controller.poll(100):
            msg = controller.recv_json()
            asbr_name, command = msg['asbr'], msg['command']

            if command and not instances.get(asbr_name):
                instances[asbr_name] = Worker(asbr_name)

    """




