#!/usr/bin/env python

import sys
import subprocess

if __name__ == '__main__':
	args = sys.argv
	if sys.argv[1] == "python":
		command = ["python.exe"]
		command.extend(sys.argv[2:])
		status = subprocess.call(command)
		sys.exit(status)
	else:
		raise Exception("don't know how to run %s" % sys.argv[1])