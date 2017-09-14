#!/usr/bin/env python

from __future__ import print_function
import logging
import subprocess
import os

def run_tool(args):
	program_files = os.environ.get("ProgramFiles(x86)", os.environ.get("ProgramFiles"))
	vswhere_path = os.path.join(program_files, "Microsoft Visual Studio", "Installer", "vswhere.exe")
	output = subprocess.check_output([vswhere_path, "-version", "[15.0, 16.0)", "-legacy", "-property", "InstallationPath"])
	vs_path = output.decode().strip()
	vcvars_path = os.path.join(vs_path, "VC", "Auxiliary", "Build", "vcvarsall.bat")
	logging.info("invoke %s" % str(args))
	name = os.path.join(os.getcwd(), "temp.bat")
	with open(name, "w") as bat:
		bat.write('set VSCMD_START_DIR=%CD%\n')
		bat.write('call "%s" %s >NUL 2>NUL\n' % (vcvars_path, "amd64"))
		bat.write(" ".join(args))
		bat.close()
	status = subprocess.call([name])
	os.unlink("temp.bat")
	return status

def ar(args):
	logging.basicConfig(level=logging.DEBUG)
	logging.info("winfigure (ar) called with arguments %s" % str(args))
	archive_name = None
	options = None
	members = []
	index = 0
	while index < len(args):
		option = args[index]
		if not options:
			# short option(s)
			options = option
			if options[0] == "-":
				options = options[1:]
			for short_option in options:
				if short_option == "c":
					# -c Create the archive
					pass
				elif short_option == "r":
					# -r Insert the files member... into archive (with replacement)
					pass
				else:
					raise Exception("unknown option %s" % option)
		elif not archive_name:
			archive_name = option
		else:
			members.append(option)
		index += 1
	lib_options = ["lib.exe"]
	lib_options.extend(members)
	lib_options.append("/OUT:%s" % archive_name)
	status = run_tool(lib_options)
	return status


def run(language, args):
	logging.basicConfig(level=logging.DEBUG)
	logging.info("winfigure called with arguments %s" % str(args))

	cl_options = ["cl.exe"]
	link_options = []
	filename = None
	index = 0
	output_name = None
	mode = "exe"
	while index < len(args):
		option = args[index]
		if len(option) == 2 and option[0] == "-":
			# short option
			short_option = option[1]
			if short_option == "c":
				# -c compile or assemble the source files, but do not link
				cl_options.append("/c") # /c Compiles without linking
				mode = "obj"
			elif short_option == "w":
				# -w Inhibit all warning messages
				cl_options.append("/w") # /w Disables all warnings
			elif short_option == "o":
				index += 1
				output_name = args[index]
			elif short_option == "O":
				pass
			elif short_option == "g":
				# Produce debugging information in the operating system's native format
				cl_options.append("/Zi") # /Zi Generates complete debugging information
			elif short_option == "E":
				# Stop after the preprocessing stage; do not run the compiler proper
				# The output is in the form of preprocessed source code, which is sent to the standard output
				cl_options.append("/EP") # /EP Copies preprocessor output to standard output
				mode = "preprocessor"
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
			elif short_option == "I":
				# Add the directory dir to the list of directories to be searched for header files
				dir = option[2:]
				cl_options.extend(["/I", dir])
			elif short_option == "L":
				dir = option[2:]
				link_options.append("/LIBPATH:%s" % dir)
			else:
				raise Exception("unknown option %s" % option)
		else:
			filename = option
		index += 1

	cl_options.append(filename)
	if output_name:
		if mode == "exe":
			cl_options.append("/Fe%s" % output_name)
		elif mode == "obj":
			cl_options.append("/Fo%s" % output_name)
		elif mode == "preprocessor":
			cl_options.append("/Fi%s" % output_name)
	if link_options:
		cl_options.append("/link")
		cl_options.extend(link_options)
	status = run_tool(cl_options)

	return status
