#!/usr/local/bin/python3

#/cgi-bin/DisplayRasmol.pl?chopping4f93B=4f93 D433-453[B]+682-889[B] D454-681[B] D890-981[B]
#D982-1123[B] D1124-1180[B] D1181-1289[B] D1290-1519[B] D1520-1725[B] D1726-1812[B] D1813-1955[B]
#D1956-2012[B] D2013-2125[B] F403-432[B];
#comparedchoppingswap=1;colouring=comparedchopping;
#id=/cath/data/current/ssapxmlsup/4f/4f93B/4f93B4bgdA.superpose.xml;
#chopping4bgdA=4bgd D451-471[A]+700-908[A] D472-699[A] D909-998[A] D999-1140[A] D1141-1198[A]
#D1199-1311[A] D1312-1540[A] D1541-1743[A] D1744-1846[A] D1847-1989[A] D1990-2049[A] D2050-2163[A]
#F442-450[A];cathversion=CV_CURRENT

import re
import cgi
import tempfile
import configparser
import traceback
import os
import sys
from random import randrange

#####IMPORTANT PREAPARATION

##function for printing out an error message
def print_err(content):
    print("Content-type: text/plain\n")
    print("This script has encountered a problem:\n")
    print(content)
    print("\nThe traceback from python:\n")
    print(traceback.format_exc())
    sys.exit()

##function for debugging and printing out the output neatly

def print_output(content, trcb): #arguments are for more text and true for traceback/else for no traceback
    print("Content-type: text/plain\n")
    print("script produced the following output (this would be printed into pml)")
    print(content)
    if trcb:
        try:
            print(traceback.format_exc())
        except:
            print("no traceback available")
    else:
        print("you didnt ask for traceback")

bindir = os.path.abspath(os.path.dirname(sys.argv[0])) #checks where process is running
config = configparser.ConfigParser() #config setup
form = cgi.FieldStorage() #cgi setup

norm_colours = [ #colours from CATH
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

tint_colours = [
 '[127.5, 127.5, 255.0]',
 '[255.0, 209.5, 127.5]',
 '[127.5, 255.0, 255.0]',
 '[214.5, 186.0, 171.5]',
 '[150.0, 196.5, 170.5]',
 '[255.0, 127.5, 177.5]',
 '[255.0, 127.5, 255.0]',
 '[255.0, 213.0, 220.5]',
 '[250.5, 250.5, 186.0]',
 '[255.0, 205.5, 127.5]',
 '[203.5, 255.0, 217.0]',
 '[255.0, 127.5, 127.5]',
 '[255.0, 162.0, 127.5]',
 '[127.5, 252.5, 182.0]',
 '[156.5, 199.5, 255.0]',
 '[246.5, 192.5, 246.5]',
 '[127.5, 255.0, 127.5]',
 '[255.0, 255.0, 127.5]',
 '[255.0, 177.5, 186.0]',
 '[191.0, 191.0, 191.0]',
 '[207.0, 143.0, 247.0]',
 '[214.5, 234.0, 255.0]',
 '[197.0, 247.0, 197.0]']


#####TAKE THE INPUTS

try: #try to find the config file
    try: #look for it in the env variables
        config_file = os.environ['DOMCHOP_PYMOL_CONFIG_FILE']
    except: #look for it in the folder
        config_file = bindir + '/' + 'config.ini'
except:
    print_err("No config file found in envir or in the folder")

config.read(config_file) #read the config file

try:
    pdb_dir = config['DEFAULT']['pdb_dir']
    is_pdb = config['DEFAULT']['is_pdb']
except:
    print_err("The config file has no proper settings")

try: #try to get the string from cgi form
    the_string = form.getvalue('chopping')
except:
    print_err("There was an issue with getting the chopping string!")

try: #try to get the string from cgi form
    the_string = form.getvalue('chopping')
except:
    print_err("There was an issue with getting the chopping string!")

if len(the_string) < 5: #check string validity
    print_err("String is too short!")

#####HANDLE INPUTS

pdb_id_wholeRegex = re.compile(r'\d\w{3}')
pdb_chainRegex = re.compile(r'\W\w\W')
whole_domainRegex = re.compile(r'D\d+-\d+\S*')
fragmentRegex = re.compile(r'F\d{1,10}-\d{1,10}')
coordinatesRegex = re.compile(r'\d+-\d+')

#creates variables from regexes
pdb_id_chain = pdb_id_wholeRegex.search(the_string).group() + (pdb_chainRegex.search(the_string).group())[1]
domains = whole_domainRegex.findall(the_string)
fragments = fragmentRegex.findall(the_string)

def fetch_domains(list_of_strings, pdb_id): #returns a dictionary of domains and coordinates
    dict_domains = {}
    count = 1  #print "%02d" % (1,)
    for string in list_of_strings:
        list_of_domains = coordinatesRegex.findall(string)
        dict_domains[pdb_id + str(count).zfill(2)] = list_of_domains
        count += 1
    return dict_domains

def fetch_fragments(list_of_fragments): #returns a list of coordinates that are fragments
    fragment_list = []
    for fragment in list_of_fragments:
        fragment_list.append(coordinatesRegex.search(fragment).group())
    return fragment_list

def set_colours(pml, norm_colours, tint):
    if tint == True:
        for colour in norm_colours:
            pml.write("\nset_colour tint_dom" + str(norm_colours.index(colour) + 1) + ", " + colour)
    elif tint == False:
        for colour in norm_colours:
            pml.write("\nset_colour dom" + str(norm_colours.index(colour) + 1) + ", " + colour)

def fetch_pdb(pdb, pdb_id, pml):#
    pml.write('\ncmd.read_pdbstr("""\\' + '\n')
    for line in pdb: #takes each line of pdb and adds it to the pml with a backslash at the end
        pml.write(line.rstrip("\n") + "\\\n")
    pml.write('""", "' + pdb_id + '")\n\n')

def add_domains(pml, source_of_domains, pdb_id):
    count = 1
    number_of_doms = len(fetch_domains(source_of_domains, pdb_id))
    for domain in range(number_of_doms):
        pml.write("select " + pdb_id + str(count).zfill(2) + ",")
        for coordin in fetch_domains(source_of_domains, pdb_id)[
                    pdb_id + str(count).zfill(2)]:
            if coordin == fetch_domains(source_of_domains, pdb_id)[pdb_id + str(count).zfill(2)][-1]:  # doesnt add a + if it is the last piece
                pml.write(" chain " + pdb_id[-1] + " and resi " + coordin)
                break
            pml.write(" chain " + pdb_id[-1] + " and resi " + coordin + " +")
        count += 1
        pml.write("\n")

#puts fragment selection in the pml
def add_fragments(pml, source_of_fragments, pdb_id):
    if len(fetch_fragments(source_of_fragments)) == 0:
        return
    pml.write("\nselect fragments, ")
    for fragment in fetch_fragments(source_of_fragments):  # puts all fragments in .pml, creating one object for them
        if fragment == fetch_fragments(source_of_fragments)[-1]:  # doesn't add a + if it is the last fragment
            pml.write("chain " + pdb_id[-1] + " & " + "resi " + fragment + "\n")
            break
        pml.write("chain " + pdb_id[-1] + " & " + "resi " + str(fragment) + " + ")

def colour_domains(pml, source_of_domains, pdb_id, tint):
    number_of_doms = len(fetch_domains(source_of_domains, pdb_id))
    count = 1
    if tint == False:
        for domain in range(number_of_doms):
            pml.write("colour dom" + str(count) + ", " + pdb_id + str(count).zfill(2) + "\n")
            count += 1
    elif tint == True:
        for domain in range(number_of_doms):
            pml.write("colour tint_dom" + str(count) + ", " + pdb_id + str(count).zfill(2) + "\n")
            count += 1

def create_pymol(): #compiles data into the pml file
    pymol_script = tempfile.TemporaryFile(mode='w+t') #creates a temporal file with the chopping
    pymol_script.write("Content-type: text/x-pymol\n") #header for CGI
    pymol_script.write("Content-Disposition: attachement; filename=" + pdb_id_chain + "_chopping" + str(randrange(10000, 99999, 1))+".pml\n")
    try:
        pdb_file = open(pdb_dir + pdb_id_chain[0:4] + is_pdb, 'r') #opens a pdb file for the protein
    except:
        print_err("PDB file not found")
    set_colours(pymol_script,norm_colours, False)
    fetch_pdb(pdb_file, pdb_id_chain[0:4], pymol_script)
    pymol_script.write("\ncolour White, all\n")
    add_domains(pymol_script, domains, pdb_id_chain)
    add_fragments(pymol_script, fragments, pdb_id_chain)
    pymol_script.write("\nselect the_rest, not chain " + pdb_id_chain[-1]) #creates the rest of the protein as an object
    pymol_script.write("\n\n")
    colour_domains(pymol_script, domains, pdb_id_chain, False)
    pymol_script.write("\ncolour White, fragments") #colours the fragments
    pymol_script.write("\ncolour gray50, the_rest") #colours the rest of the chain
    pymol_script.write("\nhide all\ndeselect\ndelete sele\n\n") #creates blank screen
    pymol_script.write("set fog_start, 0\nset depth_cue, 0\n") #visual effects
    pymol_script.write("set label_size, 12\nset label_position,(1.5,1.5,1.5)\nset label_color, gray70\n") #comnfig the labeel size, colour and location
    pymol_script.write("hide all\nshow surface, all\nshow cartoon, !the_rest\nshow ribbon the_rest\nset transparency, 0.4\n") #all of protein with surface
    pymol_script.write("zoom all\norigin all\nscene F4, store\n\n") #all of protein with surface
    pymol_script.write("hide all\nshow cartoon, !the_rest\nshow ribbon, the_rest\n")#all of protein in cartoon
    pymol_script.write("zoom all\norigin all\nscene F3, store\n\n") #all of protein in cartoon
    pymol_script.write("hide all\nshow cartoon, !the_rest\nshow surface, !the_rest\nset transparency, 0.4\n") #only chain with surface
    pymol_script.write("zoom !the_rest\norigin !the_rest\nscene F2, store\n\n") #only chain with surface
    pymol_script.write("hide all\nshow surface, all\nzoom all\norigin all\nscene F6, store\n\n")
    pymol_script.write("hide all\nshow cartoon, !the_rest\norigin !the_rest\nzoom !the_rest\nlabel n. N and !the_rest, resi\nscene F5, store\n\n") #show with labels
    pymol_script.write("hide all\nshow cartoon, !the_rest\n") #only chain in cartoon, main view
    pymol_script.write("zoom !the_rest\norigin !the_rest\nscene F1, store\n\n") #only chain in cartoon, main view
    pymol_script.write('cmd.wizard("message", "Please us F1-F6 to switch between different scenes")') #message
    pymol_script.seek(0)
    print(pymol_script.read()) #prints content of the temp file
    pdb_file.close()
    pymol_script.close()
create_pymol()
