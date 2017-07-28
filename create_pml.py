"""
this is supposed to create a .pml from a string of data
need to organise the regex into a callable function
add the pdb inside the pml
tests from perl script:
10gs D2-78[A]+187-208[A] D79-186[A] F209-209[A]
1a35A D236-319[A] D320-430[A] D431-580[A] D591-635[A]+713-764[A] F215-235[A] F581-590[A] F765-765[A]
1a36 D2-215[A]+320-431[A] D232-319[A] D432-583[A] D584-765[A]
"""

import re

the_string = '''
1a35A D236-319[A] D320-430[A] D431-580[A] D591-635[A]+713-764[A] F215-235[A] F581-590[A] F765-765[A]
'''

pdb_idRegex = re.compile(r'\w{4,5}')
whole_domainRegex = re.compile(r'D\d+-\d+\S*')
fragmentRegex = re.compile(r'F\d{1,10}-\d{1,10}')
coordinatesRegex = re.compile(r'\d+-\d+')
list_of_colours = ["Blue", "Red", "Green", "Yellow", "Pink", "Grey"]

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

def fetch_fragments(list_of_fragments): #returns a list of coordinates that are fragments
    fragment_list = []
    for fragment in list_of_fragments:
        fragment_list.append(coordinatesRegex.search(fragment).group())
    return fragment_list

def create_pymol(): #will compile all the data into a .pml file
    pymol_script = open('C:\\Users\\Ilya\\PycharmProjects\\pymol\\pymolscript.pml', 'w')
    pymol_script.write("fetch " + pdb_id[0] + ", async=0\n" + "select all\ncolour white\ndeselect\n")
    count = 1
    number_of_doms = len(fetch_domains(domains))
    for domain in range(number_of_doms):
        pymol_script.write("select domain" + str(count) + ", ")
        for coordin in fetch_domains(domains)["domain " + str(count)]:
            if coordin == fetch_domains(domains)["domain " + str(count)][-1]:
                pymol_script.write("resi " + coordin)
                break
            pymol_script.write("resi " + coordin + " + ")
        count += 1
        pymol_script.write("\n")
    for domain in range(number_of_doms):
        pymol_script.write("colour " + list_of_colours[domain] + (", domain") + str(domain + 1) + "\n")
    pymol_script.write("select fragments, ")
    for fragment in fetch_fragments(fragments):
        if fragment == fetch_fragments(fragments)[-1]:
            pymol_script.write("resi " + fragment)
            break
        pymol_script.write("resi " + str(fragment) + " + ")
    pymol_script.write("\ncolour Purple, fragments\n")
    pymol_script.write("hide all\ndeselect\nshow cartoon\ndelete sele\n")



print(pdb_id[0])
print(fetch_domains(domains))
print(fragments)


create_pymol()
