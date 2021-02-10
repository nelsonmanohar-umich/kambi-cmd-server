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
            await asyncio.sleep(random.randint(0,10))
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





async def run_this(cmd, options, path):
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
    print(f'[{cmd!r} exited with {proc.returncode}]')
    if stdout: print(f'[stdout]\n{stdout.decode()}')
    if stderr: print(f'[stderr]\n{stderr.decode()}')
    await asyncio.sleep(random.randint(0,2))
    ret, out, err = proc.returncode, stdout, stderr
    return ret, out, err







# A windowed memory to requests from each IP to
# ban/throttle IPs that are overloading this service
# a window of a maximum of nmax requests within the
# last tmax seconds is allowed.
class ServerCacheObject(object):
    def __init__(self, nmax=100, tmax=2):
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





class CmdValidator(object):
    def __init__(self, cmd = "ls",
                       valid_chars = string.ascii_letters + string.punctuation + string.whitespace + "-",
                       valid_options = "-lst1hraf",
                       banned = ("eval", "globals", "locals", "getattr", "setattr", " su ")):
        self.cmd = cmd
        self.valid_chars = valid_chars
        self.valid_options = valid_options
        self.p = re.compile("ls ([\w\\.]*)")
        self.banned = banned
        self.debug = False
        return


    def validate(self, cmdstr, cmd, options, path):
        if self.debug: print("VALIDATING", cmdstr)

        if not cmdstr != cmdstr.strip():
            if self.debug: print("Whitespace at end of command string ignored")
            cmdstr = cmdstr.strip()

        if not cmdstr.startswith(self.cmd + " "):
            return False, "invalid cmd, currently only handles %s" % self.cmd, 400
        if "../" in cmdstr:
            return False, "cannot list directories above", 403
        if len(cmdstr) > 127:
            return False, "cmd string is too long", 400
        if any([c not in self.valid_chars for c in cmdstr]):
            return False, "cmd has unexpected non-ascii characters", 400
        if self.p.findall(cmdstr) == [] and cmdstr != self.cmd:
            return False, "cmd is expecting a unix-like path", 403
        if any([dangerous_str in cmdstr for dangerous_str in self.banned]):
            return False, "cmd could be obfuscated", 404
        if eval("\"%s\"" % cmdstr, {}, {}) != cmdstr:
            return False, "cmd could possibly be an injection attack", 404

        if not all([c in self.valid_options for c in options]):
            return False, "cmd uses options other than %s" % self.valid_options, 400
        return True, "", 200








class Shutdown(Resource):
    def get(self):
        res = {'cmd': "Shutdown",
               'out': "OK"}
        # shut down service and stop receiving api calls
        # retcode, data, err = asyncio.run(run_this(cmd, options, path))
        return res, 200






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
        print("\n" * 5 + "-" * 32)
        return res


    def get(self):
        print("\n" * 3 + "-" * 32)
        reqid = ReqIdServer.getReqId()
        t_now = ReqIdServer.getTime()
        ServerCache.pending_reqids[reqid] = t_now

        try:
            cmd = request.args.get('cmd')
            path = request.args.get('path')
        except:
            data = "cmd and path params not found in request"
            retcode = 400
            res = self.format_response(reqid, str(cmd), str(data))
            return res, retcode

        try:
            options = str(request.args.get('options')).strip().replace("-", "").replace(" ", "")
            if options: options = "-" + options
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
            retcode = 401
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




class RequestIdServerObject(object):
    def __init__(self):
        self.num = 1000
        self.reqlock = Lock()
        self.starttime = time.time()
        return

    def getTime(self):
        return (time.time() - self.starttime)

    def getReqId(self):
        self.reqlock.acquire()
        self.num += 1
        self.reqlock.release()
        return self.num



if __name__ == "__main__":
    Validator = CmdValidator("ls")
    ServerCache = ServerCacheObject()
    ReqIdServer = RequestIdServerObject()
    api.add_resource(EntryPoint, '/execute')
    api.add_resource(Shutdown, '/shutdown')
    app.run(threaded=True, debug=True)



"""
The docs describe the attributes available on the request. In most common cases request.data will be empty because it's used as a fallback:
request.data Contains the incoming request data as string in case it came with a mimetype Flask does not handle.
request.args: the key/value pairs in the URL query string
request.form: the key/value pairs in the body, from a HTML post form, or JavaScript request that isn't JSON encoded
request.files: the files in the body, which Flask keeps separate from form. HTML forms must use enctype=multipart/form-data or files will not be uploaded.
request.values: combined args and form, preferring args if keys overlap
request.json: parsed JSON data. The request must have the application/json content type, or use request.get_json(force=True) to ignore the content type.

All of these are MultiDict instances (except for json). You can access values using:
request.form['name']: use indexing if you know the key exists
request.form.get('name'): use get if the key might not exist
request.form.getlist('name'): use getlist if the key is sent multiple times and you want a list of values. get only returns the first value.
"""




