#!/usr/bin/env python

from utilities.settings import CONFIG
from kafka import KafkaConsumer
import multiprocessing
import uuid
import json


class Receiver(multiprocessing.Process):

    def __init__(self, device, queue):
        super(Receiver, self).__init__()
        self._device = device
        self._queue = queue 
        self._action = multiprocessing.Event()

    def run(self):
        """Collect data from Kafka in a new process."""

        self._consumer = KafkaConsumer(self._device,
                                       group_id=uuid.uuid4(),
                                       bootstrap_servers=CONFIG["KAFKA_SERVERS"],
                                       consumer_timeout_ms=1000,
                                       auto_offset_reset="largest")

        while not self._action.is_set():
            for msg in self._consumer:
                self.send_message(msg)

    def send_message(self, msg):
        """Put message on the queue."""

        self._queue.put(msg)
 
    def stop(self):
        """Stop process when instructed."""

        self._action.set()

