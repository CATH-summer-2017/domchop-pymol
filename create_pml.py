"""
this is supposed to create a .pml from a string of data
need to organise the regex into a callable function, need to fimish the .pml compiler
test from perl script:
10gsA D2-78[A]+187-208[A] D79-186[A] F209-209[A]
1a35A D236-319[A] D320-430[A] D431-580[A] D591-635[A]+713-764[A] F215-235[A] F581-590[A] F765-765[A]
1a36A D2-215[A]+320-431[A] D232-319[A] D432-583[A] D584-765[A]
"""

import re

the_string = '''
10gsA D2-78[A]+187-208[A] D79-186[A] F209-209[A]
'''
#creates different regexes
pdb_id_wholeRegex = re.compile(r'\d\w{3}')
pdb_id_chainRegex = re.compile(r'\d\w{4}')
whole_domainRegex = re.compile(r'D\d+-\d+\S*')
fragmentRegex = re.compile(r'F\d{1,10}-\d{1,10}')
coordinatesRegex = re.compile(r'\d+-\d+')

list_of_colours = ["Blue", "Red", "Green", "Yellow", "Pink", "Grey"]

pdb_id_whole = pdb_id_wholeRegex.search(the_string).group()
pdb_id_chain = pdb_id_chainRegex.search(the_string).group()
domains = whole_domainRegex.findall(the_string)
fragments = fragmentRegex.findall(the_string)

def fetch_domains(list_of_strings):#returns a dictionary of domains and coordinates
    dict_domains = {}
    count = 1  #print "%02d" % (1,)
    for string in list_of_strings:
        list_of_domains = coordinatesRegex.findall(string)
        dict_domains[pdb_id_chain + str(count).zfill(2)] = list_of_domains
        count += 1
    return dict_domains

def fetch_fragments(list_of_fragments): #returns a list of coordinates that are fragments
    fragment_list = []
    for fragment in list_of_fragments:
        fragment_list.append(coordinatesRegex.search(fragment).group())
    return fragment_list

def create_pymol(): #will compile all the data into a .pml file
    pymol_script = open('C:\\Users\\Ilya\\PycharmProjects\\pymol\\' + pdb_id_chain +'_chopping' '.pml', 'w')
    pdb_file = open('C:\\Users\\Ilya\\PycharmProjects\\pymol\\' + pdb_id_whole + '.pdb', 'r')
    pymol_script.write('cmd.read_pdbstr("""\\' + '\n')
    for line in pdb_file:
        pymol_script.write(line.rstrip("\n") + "\\\n")
    pymol_script.write('""", "' + pdb_id_chain + '")\n\n')
    count = 1
    number_of_doms = len(fetch_domains(domains))
    for domain in range(number_of_doms): #puts all domains in .pml
        pymol_script.write("create " + pdb_id_chain + str(count).zfill(2) + ",")
        for coordin in fetch_domains(domains)[pdb_id_chain + str(count).zfill(2)]:#puts all pieces of a single domain in .pml
            if coordin == fetch_domains(domains)[pdb_id_chain + str(count).zfill(2)][-1]: #doesnt add a + if it is the last piece
                pymol_script.write(" chain " + pdb_id_chain[-1] + " and resi " + coordin)
                break
            pymol_script.write(" chain " + pdb_id_chain[-1] + " and resi " + coordin + " +")
        count += 1
        pymol_script.write("\n")
    pymol_script.write("create fragments, ")
    for fragment in fetch_fragments(fragments): #puts all fragments in .pml
        if len(fetch_fragments(fragments)) == 0:
            break
        elif fragment == fetch_fragments(fragments)[-1]: #doesn't add a + if it is the last fragment
            pymol_script.write("resi " + fragment + "\n")
            break
        pymol_script.write("resi " + str(fragment) + " + ")
    pymol_script.write("create the_rest, not chain " + pdb_id_chain[-1])
    pymol_script.write("\n\n")
    count = 1
    for domain in range(number_of_doms):
        pymol_script.write("colour " + list_of_colours[domain] + ", " + pdb_id_chain + str(count).zfill(2) + "\n")
        count += 1
    pymol_script.write("colour White, fragments\n")
    pymol_script.write("colour gray30, the_rest\n")
    pymol_script.write("zoom\ndelete " + pdb_id_chain + "\nhide all\ndisable the_rest\nselect all\nshow cartoon, all\ndelete sele\n")
    pymol_script.close()
    pdb_file.close()

print(pdb_id_whole)
print(pdb_id_chain)
print(domains)
print(fetch_domains(domains).keys())
print(fetch_fragments(fragments))

create_pymol()
