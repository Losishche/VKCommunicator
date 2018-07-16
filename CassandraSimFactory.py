#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

import requests, json, time, traceback, os, cassandra
from time import sleep
from datetime import datetime, timedelta, date, time
from threading import Timer
from multiprocessing import Process, Queue, active_children
from cassandra import ConsistencyLevel
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement, dict_factory
from cassandra.policies import RetryPolicy
from cassandra import RequestExecutionException

retry_class = RetryPolicy()
retry_class.RETRY = 200


def log_error(exc):
    print("Operation failed: {}".format(exc))


def results(res):
    print("Wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww")
    firstrow = ""
    success = False
    print(type(session.execute(query, timeout=120)))
    print(type(res))

    while not (success):
        try:
            for row in res:  # session.execute(query,timeout=120):
                if firstrow == "":
                    firstrow = row
                    print(row)
                    print(firstrow)
                if row == firstrow:
                    print("ATTENTION! REPEAT ERROR")
                    print(row)
                    print(firstrow)
                data.write("{};{};{}\n".format(row["abonent"], row["app_version"], row["operator_id"]))
            success = True
        except Exception as err:
            print(err.__class__)
            success = False
            sleep(5)

with open("Abonent_AppVersion.csv", "w") as data:
    try:
        auth_provider = PlainTextAuthProvider(username='cassandra', password='cassandra')
        cluster = Cluster([
            '172.16.100.251',
            '172.16.100.103',
            '172.16.100.230',
            '172.16.100.83',
            '172.16.100.139',
            '172.16.100.201',
            '172.16.100.202',
            '172.16.100.244',
            '172.16.100.243',
            '172.16.100.239',
            '172.16.100.238',
            '172.16.100.43',
            '172.16.100.55',
            '172.16.100.68',
            '172.16.100.79'
        ],
            compression=True,
            port=9042,
            auth_provider=auth_provider,
            protocol_version=2,
        )

        try:
            session = cluster.connect()
        except:
            print("буе")
            #log.put('Unable to connect')

        session.set_keyspace('a1s_sdp')
        session.row_factory = dict_factory

        query = SimpleStatement(
            "SELECT abonent,created,app_version,operator_id FROM abonent_profile_info_history",
            consistency_level=ConsistencyLevel.ONE,
            fetch_size=50000,
            retry_policy=retry_class
        )
        results(session.execute(query, timeout=3000))

        '''
        future = session.execute_async(query)
        while True:
            if future.add_callbacks(results, log_error):
                print("ret")
            else:
                print("empty")
            sleep(3)
            print("loop")'''
    except Exception as err:
        print(err)



