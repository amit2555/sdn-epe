#!/usr/bin/env python

CONFIG = {"DB_HOST":"mongodb://localhost:27017",
          "KAFKA_TOPIC":"openbmp.parsed.unicast_prefix",
          "NLRI":"ipv4 nlri-mpls",
          "KAFKA_SERVERS":["localhost:9092"],
         }

DEVICES = ["1.1.1.1", "2.2.2.2", "5.5.5.5"]


