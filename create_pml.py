"""
this is supposed to create a .pml from a string of data
need to organise the regex into a callable function, need to fimish the .pml compiler
test from perl script: (10gs D2-78[A]+187-208[A] D79-186[A] F209-209[A])
"""

import re

the_string = '''
10gs D2-78[A]+187-208[A] D79-186[A] F209-209[A]
'''

pdb_idRegex = re.compile(r'\w{4,5}')
whole_domainRegex = re.compile(r'D\d+-\d+\S*')
fragmentRegex = re.compile(r'F\d{1,10}-\d{1,10}')
coordinatesRegex = re.compile(r'\d+-\d+')

pdb_id = pdb_idRegex.findall(the_string)
domains = whole_domainRegex.findall(the_string)
fragments = fragmentRegex.findall(the_string)
coordinates = coordinatesRegex.findall(the_string)

def fetch_domains(list_of_strings): #returns a dictionary of domains and coordinates
    dict_domains = {}
    count = 1
    for string in list_of_strings:
        list_of_domains = coordinatesRegex.findall(string)
        dict_domains["domain " + str(count)] = list_of_domains
        count +=1
    return dict_domains

def fetch_fragments(list_of_fragments):#returns a dictionary of fragments
    dict_fragments =  {}
    count = 1
    for fragment in list_of_fragments:
        dict_fragments["fragment " + str(count)] = coordinatesRegex.findall(fragment)[0]
        count += 1
    return dict_fragments

def create_pymol(): #will compile all the data into a .pml file
    pymol_script = open('C:\\Users\\Ilya\\PycharmProjects\\pymol\\pymolscript.pml', 'w')
    pymol_script.write("fetch " + pdb_id[0] + ", async=0\n" + "select domain1, ")
    count = 1
    number_of_doms = len(fetch_domains(domains))
    for coordin in fetch_domains(domains)["domain " + str(count)]:
        if coordin == fetch_domains(domains)["domain " + str(count)][-1]:
            pymol_script.write("resi " + coordin)
            break
        pymol_script.write("resi " + coordin + " + ")
    pymol_script.write("\n")
create_pymol()
