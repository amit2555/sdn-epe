#!/usr/bin/env python

from bson.objectid import ObjectId
from utilities.utils import db_connect
from automation import tasks
import pandas as pd
import datetime


SECONDS = 120


def get_traffic_matrix(router):
    """Collects Netflow data and returns a traffic matrix."""

    COLUMNS = ['source', 'destination', 'router', 'bytes', 'bgpnexthop']
    peers = tasks.get_bgp_neighbors(router)

    with db_connect("sdn") as db:
        gen_time = datetime.datetime.utcnow() - datetime.timedelta(days=3)
        object_id = ObjectId.from_datetime(gen_time)
        result = db.netflow.find( { "_id":{"$gte":object_id},
                                    "netflow.bgp_ipv4_next_hop":{"$in":peers}
                                  } )

    traffic_matrix = [ [ record["netflow"]["ipv4_src_addr"],
                         record["netflow"]["ipv4_dst_addr"],
                         record["host"],
                         record["netflow"]["in_bytes"],
                         record["netflow"]["bgp_ipv4_next_hop"] ] for record in result ]

    df = pd.DataFrame(traffic_matrix, columns=COLUMNS)

    result = df["bytes"].groupby([
                                  df["source"],
                                  df["destination"],
                                  df["router"],
                                  df["bgpnexthop"]
                                ]).sum()
    result = result.reset_index()
    result.rename(columns={0:'total_bytes'}, inplace=True)
    result = result.sort('total_bytes', ascending=False)

    topN = result.head()
    return topN


def get_bmp_data(prefix):
    """Gathers BMP data for a given prefix."""

    with db_connect("sdn") as db:
        result = db.bmp.find( {"Prefix":prefix} )

    return list(result) 


if __name__ == "__main__":
    traffic_matrix = get_traffic_matrix("2.2.2.2")

    traffic_matrix['rate'] = (traffic_matrix['total_bytes']/float(SECONDS))*8
    top_destinations = list(traffic_matrix["destination"])
    print traffic_matrix #top_destinations

    print get_bmp_data("192.168.1.0/24")


    """
    egress_group = dict()
    for index, row in traffic_matrix.iterrows():
        subnet = tasks.get_route_entry(row["destination"]) 
        if egress_group.get(subnet):
            continue
        bmp = get_bmp_data(subnet)
        for row in bmp:
            egress_group[subnet].append( (row["Router_IP"]) )    
    """ 
