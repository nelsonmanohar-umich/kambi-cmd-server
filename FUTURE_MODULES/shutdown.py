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


class Shutdown(Resource):
    def get(self):
        res = {'cmd': "Shutdown Accepted",
               'out': "OK"}
        # shut down service and stop receiving api calls
        print("Server Shutting Down")
        ReqIdServer.shutdown.set()
        pending_requests = list(ServerCache.pending_reqids.keys())
        print("Pending Jobs", pending_requests)
        return res, 200




