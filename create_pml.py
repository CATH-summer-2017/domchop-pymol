"""
this is supposed to create a .pml from a string of data
need to organise the regex into a callable function, need to fimish the .pml compiler
test from perl script:
10gsA D2-78[A]+187-208[A] D79-186[A] F209-209[A]
1a35A D236-319[A] D320-430[A] D431-580[A] D591-635[A]+713-764[A] F215-235[A] F581-590[A] F765-765[A]
1a36A D2-215[A]+320-431[A] D232-319[A] D432-583[A] D584-765[A]
4bgdA D451-471[A]+700-908[A] D472-699[A] D909-998[A] D999-1140[A] D1141-1198[A] D1199-1311[A] D1312-1540[A] D1541-1743[A] D1744-1846[A] D1847-1989[A] D1990-2049[A] D2050-2163[A] F442-450

"""

import re

the_string = '''
1a35A D236-319[A] D320-430[A] D431-580[A] D591-635[A]+713-764[A] F215-235[A] F581-590[A] F765-765[A]
'''
#creates different regexes
pdb_id_wholeRegex = re.compile(r'\d\w{3}')
pdb_id_chainRegex = re.compile(r'\d\w{4}')
whole_domainRegex = re.compile(r'D\d+-\d+\S*')
fragmentRegex = re.compile(r'F\d{1,10}-\d{1,10}')
coordinatesRegex = re.compile(r'\d+-\d+')

dict_of_colours = { #colours from CATH
    "dom1" : "[0, 0, 255]",
    "dom2" : "[255, 0, 0]",
    "dom3" : "[0, 255, 0]",
    "dom4" : "[255, 255, 0]",
    "dom5" : "[255, 100, 117]",
    "dom6" : "[127, 127, 127]",
    "dom7" : "[159, 31, 239]",
    "dom8" : "[174, 213, 255]",
    "dom9" : "[139, 239, 139]",
    "dom10" : "[255, 164, 0]",
    "dom11" : "[0, 255, 255]",
    "dom12" : "[174, 117, 88]",
    "dom13" : "[45, 138, 86]",
    "dom14" : "[255, 0, 100]",
    "dom15" : "[255, 0, 255]",
    "dom16" : "[255, 171, 186]",
    "dom17" : "[246, 246, 117]",
    "dom18" : "[255, 156, 0]",
    "dom19" : "[152, 255, 179]",
    "dom20" : "[255, 69, 0]",
    "dom21" : "[0, 250, 109]",
    "dom22" : "[58, 144, 255]",
    "dom23" : "[238, 130, 238]"

}
list_of_colours = ["dom1", "dom2", "dom3", "dom4", "dom5", "dom6", "dom7", "dom8", "dom9", "dom10","dom11", "dom12", "dom13", "dom14", "dom15", "dom16", "dom17", "dom18", "dom19", "dom20", "dom21", "dom22", "dom23"]

pdb_id_whole = pdb_id_wholeRegex.search(the_string).group()
pdb_id_chain = pdb_id_chainRegex.search(the_string).group()
domains = whole_domainRegex.findall(the_string)
fragments = fragmentRegex.findall(the_string)


def fetch_domains(list_of_strings): #returns a dictionary of domains and coordinates
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

def set_colours(file_name): #sets domain colours to ones in CATH
    for colour in list_of_colours:
        file_name.write("set_colour " + colour + ", " + dict_of_colours[colour] + "\n")

def add_backslash(pdb, pdb_id, pml):#takes pdb and adds it to the pml
    for line in pdb: #takes each line of pdb and adds it to the pml with a backslash at the end
        pml.write(line.rstrip("\n") + "\\\n")
    pml.write('""", "' + pdb_id + '")\n\n')

def add_domains(pml, source_of_domains):#creates a selection for each domain
    count = 1
    number_of_doms = len(fetch_domains(source_of_domains))
    for domain in range(number_of_doms):  # puts each domains in .pml, creating a separate object
        pml.write("select " + pdb_id_chain + str(count).zfill(2) + ",")
        for coordin in fetch_domains(source_of_domains)[
                    pdb_id_chain + str(count).zfill(2)]:  # puts all pieces of a single domain in .pml
            if coordin == fetch_domains(source_of_domains)[pdb_id_chain + str(count).zfill(2)][
                -1]:  # doesnt add a + if it is the last piece
                pml.write(" chain " + pdb_id_chain[-1] + " and resi " + coordin)
                break
            pml.write(" chain " + pdb_id_chain[-1] + " and resi " + coordin + " +")
        count += 1
        pml.write("\n")

def add_fragments(pml, source_of_fragments): #creates a selection for fragments
    pml.write("\nselect fragments, ")
    for fragment in fetch_fragments(source_of_fragments):  # puts all fragments in .pml, creating one object for them
        if len(fetch_fragments(source_of_fragments)) == 0:
            break
        elif fragment == fetch_fragments(source_of_fragments)[-1]:  # doesn't add a + if it is the last fragment
            pml.write("resi " + fragment + "\n")
            break
        pml.write("resi " + str(fragment) + " + ")

def colour_domains(pml, source_of_domains): #colours the selected domains
    number_of_doms = len(fetch_domains(source_of_domains))
    count = 1
    for domain in range(number_of_doms):  # colours the domains
        pml.write("colour " + list_of_colours[domain] + ", " + pdb_id_chain + str(count).zfill(2) + "\n")
        count += 1

def create_pymol(): #compiles data into the pml file
    pymol_script = open('C:\\Users\\Ilya\\PycharmProjects\\pymol\\Pymol Scripts\\' + pdb_id_chain +'_chopping_testsuper' '.pml', 'w') #creates the file
    pdb_file = open('C:\\Users\\Ilya\\PycharmProjects\\pymol\\PDB files\\' + pdb_id_whole + '.pdb', 'r') #opens a pdb file for the protein
    set_colours(pymol_script)
    add_backslash(pdb_file, pdb_id_whole, pymol_script)
    add_domains(pymol_script, domains)
    add_fragments(pymol_script, fragments)
    pymol_script.write("\nselect the_rest, not chain " + pdb_id_chain[-1]) #creates the rest of the protein as an object
    pymol_script.write("\n\n")
    colour_domains(pymol_script, domains)
    pymol_script.write("colour White, fragments\n") #colours the fragments
    pymol_script.write("colour gray70, the_rest\n")#colours the rest of the chain
    pymol_script.write("\nhide all\ndeselect\ndelete sele\n\n")#creates blank screen
    pymol_script.write("hide all\nshow surface, all\nshow cartoon, all\nset transparency, 0.1\nzoom\nscene F4, store\n\n")#all of protein with surface
    pymol_script.write("hide all\nshow cartoon, all\nzoom\nscene F3, store\n\n")#all of protein in cartoon
    pymol_script.write("hide all\nshow cartoon, !the_rest\nshow surface, !the_rest\nset transparency, 0.1\nzoom\nscene F2, store\n\n") #only chain with surface
    pymol_script.write("hide all\nshow cartoon, !the_rest\nzoom\nscene F1, store\n\n") #only chain in cartoon
    pymol_script.write("set fog_start, 0\nset depth_cue, 0\n")#visual effects
    pymol_script.write('cmd.wizard("message", "Please us F1-F4 to switch between different scenes")')
    pymol_script.close()
    pdb_file.close()

print("PDb ID = " + pdb_id_whole)
print("Chain ID = " + pdb_id_chain)
print("Number of domains = " + str(len(fetch_domains(domains))))
print("Domain list: ")
print(domains)
print("Fragments list: ")
print(fetch_fragments(fragments))

create_pymol()
