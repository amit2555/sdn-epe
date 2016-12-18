#!/usr/bin/env python

from utilities.settings import CONFIG
from utilities.utils import db_connect 
from collect.receiver import Receiver
import multiprocessing
import logging
import pymongo


logger = logging.getLogger("Controller")
logging.basicConfig(level=logging.DEBUG)
q = multiprocessing.Queue()


class Router(object):

    def __init__(self, device):
        self.device = device
        self.receiver = Receiver(self.device, q)

    def update_status(self, status):
        self.prefixes = dict()
        if status == "up":
            self.receiver.start()
        if status == "down":
            self.receiver.stop()

    def prefix_announced(self, bgp_update):
        """Update BGP-LU Prefixes announced in BGP Update."""

        for nexthop in bgp_update["announce"][CONFIG["NLRI"]]: 
            for prefix in bgp_update["announce"][CONFIG["NLRI"]][nexthop]:
                self.prefixes[prefix] = self.prefixes.get(prefix, {})
                self.prefixes[prefix].update({
                            "nexthop":nexthop,
                            "labels" :bgp_update["announce"][CONFIG["NLRI"]][nexthop][prefix]["label"]})
                self.prefixes[prefix].update(bgp_update["attribute"])

                self._get_mpls_data_for_prefix(prefix)

        logger.debug(self.__dict__)

    def prefix_withdrawn(self, bgp_update):
        """Remove BGP-LU Prefixes withdrawn in BGP Update."""

        for prefix in bgp_update["withdraw"][CONFIG["NLRI"]]:
            self.prefixes.pop(prefix)

    def _get_mpls_data_for_prefix(self, prefix):
        """Get outgoing interface from MPLS LFIB for prefix."""

        with db_connect("sdn") as db:
            result = db.mpls.find({ "device":self.device,
                                    "prefix":prefix,
                                  }).sort("_id",pymongo.DESCENDING).limit(1)
            data = list(result)[0]
        self.prefixes[prefix].update({"interface":data["interface"]})


    def prefix_interface_update(self, data):
        """Update BGP-LU Prefixes' Interface data from Collector."""

        for elem in data:
            for prefix in self.prefixes:
                if elem['name'] == self.prefixes[prefix].get('interface'):
                    self.prefixes[prefix].update({'input_util':elem['input_util'],
                                                  'output_util':elem['output_util']})
        logger.debug(self.prefixes)


