#!/usr/bin/env python

from utilities.utils import sub_bind, sub_connect
import logging


logger = logging.getLogger('Controller')
logging.basicConfig(level=logging.DEBUG)


class ASBRPrefix(object):
    NLRI = 'ipv4 nlri-mpls'

    def __init__(self, asbr):
        self.asbr = asbr
        self.status = None 
        self.prefixes = dict()

    def update_status(self, status):
        self.status = status

    def prefix_announced(self, bgp_update):
        """Update BGP-LU Prefixes announced in BGP Update."""

        for nexthop in bgp_update['announce'][ASBRPrefix.NLRI]: 
            for prefix in bgp_update['announce'][ASBRPrefix.NLRI][nexthop]:
                self.prefixes[prefix] = self.prefixes.get(prefix, {})
                self.prefixes[prefix].update({
                            'nexthop':nexthop,
                            'labels': bgp_update['announce'][ASBRPrefix.NLRI][nexthop][prefix]['label']})
                self.prefixes[prefix].update(bgp_update['attribute'])
        logger.debug(self.prefixes)


    def prefix_withdrawn(self, bgp_update):
        """Remove BGP-LU Prefixes withdrawn in BGP Update."""

        for prefix in bgp_update['withdraw'][ASBRPrefix.NLRI]:
            self.prefixes.pop(prefix)


    def prefix_mpls_update(self, data):
        """Update BGP-LU Prefixes' MPLS data from Collector."""

        for elem in data:
            if self.prefixes.get(elem['prefix']):
                self.prefixes[elem['prefix']].update({'interface':elem['interface']})


    def prefix_interface_update(self, data):
        """Update BGP-LU Prefixes' Interface data from Collector."""

        for elem in data:
            for prefix in self.prefixes:
                if elem['name'] == self.prefixes[prefix].get('interface'):
                    self.prefixes[prefix].update({'input_util':elem['input_util'],
                                                  'output_util':elem['output_util']})
        logger.debug(self.prefixes)


def main():

    instances = dict()

    # Socket used to pull device, status from Exabgp 
    device_puller = sub_connect(5000)

    # Socket used to collect data from Collector
    collector = sub_bind(5001)

    # Socket used to collect BGP Updates from Exabgp
    update_puller = sub_connect(6000)

    while True:
        if device_puller.poll(100):
            device = device_puller.recv_json()
            asbr_name, status = device['name'], device['status']

            if not instances.get(asbr_name):
                instances[asbr_name] = ASBRPrefix(asbr_name)
            instances[asbr_name].update_status(status)

        if collector.poll(100):
            msg = collector.recv_json()
            asbr_name = msg['name']

            if instances.get(asbr_name):
                if msg['type'] == 'mpls':
                    instances[asbr_name].prefix_mpls_update(msg['data'])

                if msg['type'] == 'util':
                    instances[asbr_name].prefix_interface_update(msg['data'])

        if update_puller.poll(100):
            msg = update_puller.recv_json()
            asbr_name = msg['ip']
            bgp_update = msg['message']['update']

            if instances.get(asbr_name):
                if 'announce' in bgp_update:
                    instances[asbr_name].prefix_announced(bgp_update)

                if 'withdraw' in bgp_update:
                    instances[asbr_name].prefix_withdrawn(bgp_update)


if __name__ == "__main__":
    main()

