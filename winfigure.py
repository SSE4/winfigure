#!/usr/bin/env python

from __future__ import print_function
import logging
import subprocess
import os

def run_cl(args):
	program_files = os.environ.get("ProgramFiles(x86)", os.environ.get("ProgramFiles"))
	vswhere_path = os.path.join(program_files, "Microsoft Visual Studio", "Installer", "vswhere.exe")
	output = subprocess.check_output([vswhere_path, "-version", "[15.0, 16.0)", "-legacy", "-property", "InstallationPath"])
	vs_path = output.decode().strip()
	vcvars_path = os.path.join(vs_path, "VC", "Auxiliary", "Build", "vcvarsall.bat")
	command = ["cl.exe"]
	command.extend(args)
	logging.info("invoke cl.exe %s" % str(command))
	name = os.path.join(os.getcwd(), "temp.bat")
	with open(name, "w") as bat:
		bat.write('set VSCMD_START_DIR=%CD%\n')
		bat.write('call "%s" %s\n' % (vcvars_path, "amd64"))
		bat.write(" ".join(command))
		bat.close()
	status = subprocess.call([name])
	#os.unlink("temp.bat")
	return status

def run(language, args):
	logging.basicConfig(level=logging.DEBUG)
	logging.info("winfigure called with arguments %s" % str(args))

	cl_options = []
	filename = None
	index = 0
	output_name = None
	while index < len(args):
		option = args[index]
		if len(option) == 2 and option[0] == "-":
			# short option
			short_option = option[1]
			if short_option == "c":
				# -c compile or assemble the source files, but do not link
				cl_options.append("/c") # /c Compiles without linking
			elif short_option == "w":
				# -w Inhibit all warning messages
				cl_options.append("/w") # /w Disables all warnings
			elif short_option == "o":
				index += 1
				output_name = args[index]
			elif short_option == "O":
				pass
			else:
				raise Exception("unknown option %s" % option)
		elif len(option) > 2 and option[0] == "-" and option[1] == "-":
			# long option
			long_option = option[2:]
			raise Exception("unknown option %s" % option)
		elif len(option) > 2 and option[0] == "-":
			# short option with parameter attached, like -D_DUMMY (define)
			short_option = option[1]
			if short_option == "D":
				define = option[2:]
				if "=" in define:
					cl_options.append("/D%s" % define)
				else:
					cl_options.append("/D%s=" % define)
			else:
				raise Exception("unknown option %s" % option)
		else:
			filename = option
		index += 1

	options = cl_options
	options.append(filename)
	if output_name:
		options.append("/Fe%s" % output_name)
	status = run_cl(options)

	return status
