__doc__ = """
"""


# throtles request to a maximum of nmax (100) jobs within a window of tmax (1) seconds.
NMAX, TMAX  = 100, 1


from flask import Flask
from flask_restful import Resource, Api
from flask import request
from flask_restful import reqparse
import os
import sys
import re
import time
import glob
import string
import threading
import subprocess
import asyncio
import random
from threading import Lock, Event
import queue


# A windowed memory to requests from each IP to
# ban/throttle IPs that are overloading this service
# a window of a maximum of nmax requests within the
# last tmax seconds is allowed.
class ServerCacheObject(object):
    def __init__(self, nmax=NMAX, tmax=TMAX):
        self.cache = {}
        self.history = {}
        self.starttime = time.time()
        self.nmax = nmax
        self.tmax = tmax
        self.debug = False
        self.throtled = {}
        self.pending_reqids = {}
        return


    def throtle(self, ip, nsecs=1):
        # throtled_lock not needed at this time for this demo
        if ip in self.throtled:
            t_old = self.throtled[ip]
            t_now = time.time() - self.starttime
            t_min = t_now - nsecs
            if t_min <= t_old <= t_now:
                return True
            else:
                self.history[ip] = []
                del self.throtled[ip]

        if ip in self.history:
            if len(self.history[ip]) > self.nmax + 1:
                t_old, v = self.history[ip][0]
                t_now = time.time() - self.starttime
                t_min = t_now - self.tmax
                if t_min <= t_old <= t_now:
                    self.throtled[ip] = t_now
                    return True
        return False


    def put(self, ip, data, n=5):
        if ip not in self.history:
            self.history[ip] = []
        t_now = time.time() - self.starttime
        self.history[ip].append([t_now, data])
        print('RECENT REQUESTS FROM IP:', ip)
        for t, d in self.history[ip][-n:]:
            print("%16s" % ip, "%7.3f secs" % round(t, 3), "data=%s" % str(d))
        print('-' * 32)
        return



if __name__ == "__main__":
    ServerCache = ServerCacheObject()

