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


app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('cmd', type=str, help='ls')
parser.add_argument('options', type=str, help='any combination of -,l,h,t,r,s,a options')
parser.add_argument('path', type=str, help='a valid linux path')




class RequestIdServerObject(object):
    def __init__(self):
        self.num = 1000
        self.reqlock = Lock()
        self.starttime = time.time()
        self.shutdown = Event()
        self.shutdown.clear()
        return

    def getTime(self):
        return (time.time() - self.starttime)

    def getReqId(self):
        if not self.shutdown.is_set():
            self.reqlock.acquire()
            self.num += 1
            self.reqlock.release()
            return self.num
        else:
            return -1



if __name__ == "__main__":
    ReqIdServer = RequestIdServerObject()



