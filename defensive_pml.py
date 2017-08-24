#!/usr/bin/python3

import re
import cgi
import tempfile
import configparser
import os
import sys
import traceback
from random import randrange

###IMPORTANT PREREQUISITES

def print_err():
	print("Content-type: text/plain\n")
	print("The script encountered the following problem:\n")
	print(traceback.format_exc())
	sys.exit()

bindir = os.path.abspath(os.path.dirname(sys.argv[0]))
config = configparser.ConfigParser()
form = cgi.FieldStorage()
norm_colours = [
	'[0, 0, 255]',
	'[255, 0, 0]',
	'[0, 255, 0]',
	'[255, 255, 0]',
	'[255, 100, 117]',
	'[127, 127, 127]',
	'[159, 31, 239]',
	'[174, 213, 255]',
	'[139, 239, 139]',
	'[255, 164, 0]',
	'[0, 255, 255]',
	'[174, 117, 88]',
	'[45, 138, 86]',
	'[255, 0, 100]',
	'[255, 0, 255]',
	'[255, 171, 186]',
	'[246, 246, 117]',
	'[255, 156, 0]',
	'[152, 255, 179]',
	'[255, 69, 0]',
	'[0, 250, 109]',
	'[58, 144, 255]',
	'[238, 130, 238]']

###INPUTS

try:
	config.read(bindir + '/' + 'config.ini')
except:
	print_err()

try:
	pdb_dir = config['DEFAULT']['pdb_dir']
except:
	print_err()

try:
	is_pdb = config['DEFAULT']['is_pdb']
except:
	print_err()

try:
    the_string = form.getvalue('chopping')
except:
    print("Conten-type: text/plain\n" + e)

print("Content-type: text/plain\n")
print(the_string)
