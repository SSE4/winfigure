#!/usr/bin/env python

import winfigure
import sys

if __name__ == '__main__':
	status = winfigure.run(language='cxx', args=sys.argv[1:])
	sys.exit(status)
