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




class CmdValidator(object):
    def __init__(self, cmd = "ls",
                       valid_chars = string.ascii_letters + string.punctuation + string.whitespace + "-",
                       valid_options = "-lst1hrafR",
                       banned = ("eval", "globals", "locals", "getattr", "setattr", " su ")):
        self.cmd = cmd
        self.valid_chars = valid_chars
        self.valid_options = valid_options
        self.p = re.compile("ls ([\w\\.]*)")
        self.banned = banned
        self.debug = True
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
            return False, "cmd string is too long", 414
        if any([c not in self.valid_chars for c in cmdstr]):
            return False, "cmd has unexpected characters", 406
        if self.p.findall(cmdstr) == [] and cmdstr != self.cmd:
            return False, "cmd is expecting a unix-like path", 403
        if any([dangerous_str in cmdstr for dangerous_str in self.banned]):
            return False, "cmd could be obfuscated", 404
        if eval("\"%s\"" % cmdstr, {}, {}) != cmdstr:
            return False, "cmd could possibly be an injection attack", 404
        if not all([c in self.valid_options for c in options]):
            return False, "cmd uses options other than %s" % self.valid_options, 400
        return True, "", 200








if __name__ == "__main__":
    Validator = CmdValidator("ls")




