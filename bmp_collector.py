#!/usr/bin/env python

from kafka import KafkaConsumer
from utilities.utils import db_connect
from utilities.settings import CONFIG


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

    consumer = KafkaConsumer(CONFIG["KAFKA_TOPIC"])
    with db_connect("sdn") as db:
        for msg in consumer:
            structured_row = structure_data(msg[6].splitlines()[5])
            if structured_row["Action"] == "del":
                db.bmp.remove( {"Router_IP":structured_row["Router_IP"],
                                "Prefix":structured_row["Prefix"],
                                "Peer_IP":structured_row["Peer_IP"],
                                "Peer_ASN":structured_row["Peer_ASN"]
                               } ) 
            db.bmp.insert(structured_row)


if __name__ == "__main__":
    main()
