#!/usr/bin/env python

from kafka import KafkaConsumer
from elasticsearch import Elasticsearch
import uuid


def structure_data(row):
    fields = ['Action',
    'Sequence',
    'Hash',
    'Router_Hash',
    'Router_IP',
    'Base_Attr_Hash',
    'Peer_Hash',
    'Peer_IP',
    'Peer_ASN',
    'Timestamp',
    'Prefix',
    'PrefixLen',
    'isIPv4',
    'Origin',
    'AS_Path',
    'AS_Path_Count',
    'Origin_AS',
    'Next_Hop',
    'MED',
    'Local_Pref',
    'Aggregator',
    'Community_List',
    'Ext_Community_List',
    'Cluster_List',
    'isAtomicAgg',
    'isNextHopIPv4',
    'Originator_Id']

    d = dict()
    for k,v in zip(fields, row.split('\t')):
        d[k] = str(v)
    d['Prefix'] = d['Prefix'] + '/' + d['PrefixLen']
    d.pop('PrefixLen')
    return d


def main():
    INDEX_NAME = 'openbmp'
    TYPE_NAME = 'unicast_prefix'
    TOPIC_NAME = 'openbmp.parsed.unicast_prefix'

    es = Elasticsearch([{'host':'localhost', 'port':9200}])
    consumer = KafkaConsumer(TOPIC_NAME)

    for msg in consumer:
        structured_row = structure_data(msg[6].splitlines()[5])        
        es.index(index=INDEX_NAME, doc_type=TYPE_NAME, id=uuid.uuid4(), body=structured_row)


if __name__ == "__main__":
    main()
