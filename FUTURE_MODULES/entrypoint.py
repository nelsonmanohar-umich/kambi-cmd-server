__doc__ = """
A Very Basic Rest API for Remote Executing a Command

    For each operand that names a file of a type other than directory, ls displays its name as
    well as any requested, associated information.  For each operand that names a file of type
    directory, ls displays the names of files contained within that directory, as well as any
    requested, associated information.
    This simple program implements a basic API to execute a command on a remote server.

    It uses a get command with parameters, e.g.,

        - 1) EXECUTE   http://127.0.0.1:5000/execute?cmd="ls"&options="-lhstra1R"&path="./TEST"

        - 2) SHUTDOWN  http://127.0.0.1:5000/shutdown

    Valid options are:

        -l -h -s -t -r -R -a -1

Limitations
    It imposes a number of most basic (from the hip) security checks to the command against attacks.
    It throtles request to a maximum of nmax (100) jobs within a window of tmax (1) seconds.
    It remembers the current pending jobs.
    It limits the number of directories to list to one.
    It executes every request on a separate thread.
    It executes every command in a restricted shell.
    It imposes check on valid options passed.
    Testing is currently functionally based, by hand --- waiting to be migrated to unittest
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




async def request_handler_function(reqid, cmdstr, ip, cmd, options, path):
    # validate the request to weed out basic attack/exploit vectors
    valid, rejection, retcode = Validator.validate(cmdstr, cmd, options, path)
    if valid:
        print("*** ACCEPTED CMD", ip, cmdstr, "-->", valid, rejection)
        data = "None"
        if not path.strip() or os.path.exists(path) or glob.glob(path):
            # launch request into thread
            assert "ls" in cmd, "ls is the only allowed command"
            try:
                cmdstr = "%s %s %s" % ("ls ", options, path)
                cmdstr = '/bin/bash --restricted --norc --noprofile -c \" %s "' % cmdstr
            except:
                cmdstr = "%s %s %s" % ("/bin/ls ", options, path)
                cmdstr = '/bin/bash --norc --noprofile -c \" %s "' % cmdstr
            print("EXECUTING", cmdstr)
            proc = await asyncio.create_subprocess_shell(
                                 cmdstr,
                                 stdout=asyncio.subprocess.PIPE,
                                 stderr=asyncio.subprocess.PIPE)
            stdout, stderr = await proc.communicate()
            if reqid % 10 == 0:
                await asyncio.sleep(random.randint(0,3))
            print(f'[{cmd!r} exited with {proc.returncode}]')
            if stdout: print(f'[stdout]\n{stdout.decode()}')
            if stderr: print(f'[stderr]\n{stderr.decode()}')
            os_ret, os_out, os_err = proc.returncode, stdout, stderr
            data = os_out if os_ret == 0 else os_err
            retcode = 200 if os_ret == 0 else 500
        else:
            retcode = 404
        return cmdstr, data, retcode
    else:
        data = rejection
        return cmdstr, data, retcode

    retcode = 501
    return cmdstr, data, retcode










class EntryPoint(Resource):
    def format_response(self, reqid, cmdstr, data):
        print("COMPLETED: ", reqid, str(cmdstr))
        try:
            res = {'cmd': str(cmdstr),
                   'rid': str(reqid),
                   'out': str(data)}
        except:
            res = {'cmd': str.translate(str(cmdstr), "unicode"),
                   'rid': str(reqid),
                   'out': str.translate(str(data), "unicode")}
        print("\n" * 2 + "-" * 32)
        return res


    def get(self):
        print("\n" * 5 + "-" * 32)
        reqid = ReqIdServer.getReqId()
        if reqid == -1:
            data = "server is shutting down. not accepting requests"
            retcode = 418
            res = self.format_response(reqid, str("Rejected"), str(data))
            return res, retcode
        t_now = ReqIdServer.getTime()
        ServerCache.pending_reqids[reqid] = t_now

        cmd, options, path = "", "", ""
        try:
            if request.args.get('cmd') is not None:
                cmd = request.args.get('cmd')
            else:
                cmd = ""
            if request.args.get('path') is not None:
                path = request.args.get('path')
            else:
                path = ""
        except:
            data = "cmd and path params not found in request"
            retcode = 400
            res = self.format_response(reqid, str(cmd), str(data))
            del ServerCache.pending_reqids[reqid]
            return res, retcode

        try:
            if request.args.get('options') is not None:
                options = str(request.args.get('options')).strip().replace("-", "").replace(" ", "")
                if options: options = "-" + options
            else:
                options = ""
        except:
            print("*** problem with parsing options")
            options = ""

        try:
            ip = request.remote_addr
        except:
            print("*** Who are you?, What are you?, Help!")

        res, retcode = self.request_handler(reqid, ip, cmd, options, path)
        return res, retcode


    def request_handler(self, reqid, ip, cmd, options, path):
        # assembled the command from json params
        cmdstr = "%s %s %s" % (cmd, options, path)

        # update windowed history for this ip
        ServerCache.put(ip, cmdstr)

        # throtle the request if too many requests from this ip are made within a time window
        if ServerCache.throtle(ip):
            data = "Try later, too many requests from ip within recent window"
            retcode = 429
            res = self.format_response(reqid, cmdstr, data)
        else:
            cmdstr, data, retcode = asyncio.run(
                                     request_handler_function(reqid, cmdstr, ip, cmd, options, path))
            res = self.format_response(reqid, cmdstr, data)

        # update our history of pending jobs
        del ServerCache.pending_reqids[reqid]
        pending_requests = list(ServerCache.pending_reqids.keys())
        print("Pending Jobs", pending_requests)

        return res, retcode




if __name__ == "__main__":
    ReqIdServer = RequestIdServerObject()


