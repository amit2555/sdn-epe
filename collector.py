#!/usr/bin/env python

from automation import tasks
from multiprocessing import Process
from utils import sub_connect
import time
import json
import zmq
import random


class Collector:
    LOOP_DELAY = 10
    BIND_DELAY = 1 

    def __init__(self, device, port):
        self.device = device
        self.port = str(port)
        self.ctx = None
        self.sock = None 
        self.not_setup = True

    def collect(self):
        while True:
            time.sleep(Collector.LOOP_DELAY + random.random())

            if self.not_setup:
                self._deferred_setup()

            response1 = tasks.get_mpls_table(self.device)
            self.sock.send_json({'name':self.device, 'type':'mpls', 'data':response1})
            response2 = tasks.get_interfaces_utilization(self.device)
            self.sock.send_json({'name':self.device, 'type':'util', 'data':response2})


    def _deferred_setup(self):
        self.ctx = zmq.Context()
        self.sock = self.ctx.socket(zmq.PUB)
        self.sock.connect('tcp://127.0.0.1:' + self.port)
        time.sleep(Collector.BIND_DELAY)
        self.not_setup = False


def main():

    port = 5001
    instances = dict()
    previous_devices = list()
    sock = sub_connect(5000)

    while True:
        if sock.poll(100):
            device = sock.recv_json()
            print device
            #name, port, status = device['name'], device['port'], device['status']
            name, status = device['name'], device['status']

            if status == 'up':
                if not instances.get(name):            
                    instances[name] = {'instance':Collector(name, port)}
                    p = Process(target=instances[name]['instance'].collect)
                    instances[name].update({'process':p})
                    p.start()

            if status == 'down':
                if instances.get(name):
                    instances[name]['process'].terminate()
                    instances.pop(name)
                print instances


if __name__ == "__main__":
    main()

