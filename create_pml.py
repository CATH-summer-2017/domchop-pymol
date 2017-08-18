"""
this is supposed to create a .pml from a string of data
need to organise the regex into a callable function, need to fimish the .pml compiler
test from perl script:
10gsA D2-78[A]+187-208[A] D79-186[A] F209-209[A]
1a35A D236-319[A] D320-430[A] D431-580[A] D591-635[A]+713-764[A] F215-235[A] F581-590[A] F765-765[A]
1a36A D2-215[A]+320-431[A] D232-319[A] D432-583[A] D584-765[A]
4bgdA D451-471[A]+700-908[A] D472-699[A] D909-998[A] D999-1140[A] D1141-1198[A] D1199-1311[A] D1312-1540[A] D1541-1743[A] D1744-1846[A] D1847-1989[A] D1990-2049[A] D2050-2163[A] F442-450
1bvsA D1-65[A] D66-148[A] D149-199[A] F200-203[A]
1cukA D1-66[A] D67-142[A] D156-203[A]
"""

import re

the_string = '''
4bgdA D451-471[A]+700-908[A] D472-699[A] D909-998[A] D999-1140[A] D1141-1198[A] D1199-1311[A] D1312-1540[A] D1541-1743[A] D1744-1846[A] D1847-1989[A] D1990-2049[A] D2050-2163[A] F442-450

'''
#creates different regexes
pdb_id_chainRegex = re.compile(r'\d\w{4}')
whole_domainRegex = re.compile(r'D\d+-\d+\S*')
fragmentRegex = re.compile(r'F\d{1,10}-\d{1,10}')
coordinatesRegex = re.compile(r'\d+-\d+')

#colours from CATH
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
    '[238, 130, 238]'
]

pdb_id_chain = pdb_id_chainRegex.search(the_string).group()
domains = whole_domainRegex.findall(the_string)
fragments = fragmentRegex.findall(the_string)

#returns a dictionary of domains and respective coordinates
def fetch_domains(list_of_strings):
    dict_domains = {}
    count = 1
    for string in list_of_strings:
        list_of_domains = coordinatesRegex.findall(string)
        dict_domains[pdb_id_chain + str(count).zfill(2)] = list_of_domains
        count += 1
    return dict_domains

#returns a list of fragments
def fetch_fragments(list_of_fragments):
    fragment_list = []
    for fragment in list_of_fragments:
        fragment_list.append(coordinatesRegex.search(fragment).group())
    return fragment_list

#puts colours from CATH into pml
def set_colours(pml):
    for colour in norm_colours:
        pml.write("\nset_colour dom" + str(norm_colours.index(colour)+1)+", "+colour)

#puts pdb info into the pml file
def fetch_pdb(pdb, pdb_id, pml):#
    pml.write('\ncmd.read_pdbstr("""\\' + '\n')
    for line in pdb: #takes each line of pdb and adds it to the pml with a backslash at the end
        pml.write(line.rstrip("\n") + "\\\n")
    pml.write('""", "' + pdb_id + '")\n\n')

#creates selection of each domain in pml
def add_domains(pml, source_of_domains):
    count = 1
    number_of_doms = len(fetch_domains(source_of_domains))
    for domain in range(number_of_doms):  # puts each domains in .pml, creating a separate object
        pml.write("select " + pdb_id_chain + str(count).zfill(2) + ",")
        for coordin in fetch_domains(source_of_domains)[
                    pdb_id_chain + str(count).zfill(2)]:  # puts all pieces of a single domain in .pml
            if coordin == fetch_domains(source_of_domains)[pdb_id_chain + str(count).zfill(2)][-1]:  # doesnt add a + if it is the last piece
                pml.write(" chain " + pdb_id_chain[-1] + " and resi " + coordin)
                break
            pml.write(" chain " + pdb_id_chain[-1] + " and resi " + coordin + " +")
        count += 1
        pml.write("\n")

#puts fragment selection in the pml
def add_fragments(pml, source_of_fragments):
    pml.write("\nselect fragments, " + "chain " + pdb_id_chain[-1] + " and ")
    if len(fetch_fragments(source_of_fragments)) == 0:
        return
    for fragment in fetch_fragments(source_of_fragments):  # puts all fragments in .pml, creating one object for them
        if fragment == fetch_fragments(source_of_fragments)[-1]:  # doesn't add a + if it is the last fragment
            pml.write("resi " + fragment + "\n")
            break
        pml.write("resi " + str(fragment) + " + ")

#colours the domains according to the chopping
def colour_domains(pml, source_of_domains):
    number_of_doms = len(fetch_domains(source_of_domains))
    count = 1
    for domain in range(number_of_doms):  # colours the domains
        pml.write("colour dom" + str(count) + ", " + pdb_id_chain + str(count).zfill(2) + "\n")
        count += 1

#gets info about the chopped chain
def print_info():
    print("Chain ID = " + pdb_id_chain)
    print("Number of domains = " + str(len(fetch_domains(domains))))
    print("Domains: ")
    print(fetch_domains(domains))
    print("Fragments list: ")
    print(fetch_fragments(fragments))

def create_pymol(): #compiles data into the pml file
    pymol_script = open('C:\\Users\\Ilya\\PycharmProjects\\pymol\\Pymol Scripts\\' + pdb_id_chain +'_chopping' '.pml', 'w') #creates the file
    pdb_file = open('C:\\Users\\Ilya\\PycharmProjects\\pymol\\PDB files\\' + pdb_id_chain[0:4] + '.pdb', 'r') #opens a pdb file for the protein
    set_colours(pymol_script)
    fetch_pdb(pdb_file, pdb_id_chain[0:4], pymol_script)
    add_domains(pymol_script, domains)
    add_fragments(pymol_script, fragments)
    pymol_script.write("\nselect the_rest, not chain " + pdb_id_chain[-1]) #creates the rest of the protein as an object
    pymol_script.write("\n\n")
    colour_domains(pymol_script, domains)
    pymol_script.write("\ncolour White, fragments") #colours the fragments
    pymol_script.write("\nspectrum count, rainbow, the_rest")#colours the rest of the chain
    pymol_script.write("\nhide all\ndeselect\ndelete sele\n\n")#creates blank screen
    pymol_script.write("hide all\nshow surface, all\nshow cartoon, all\nset transparency, 0.1\nzoom\nscene F4, store\n\n")#all of protein with surface
    pymol_script.write("hide all\nshow cartoon, !the_rest\nshow ribbon, the_rest\nzoom\nscene F3, store\n\n")#all of protein in cartoon
    pymol_script.write("hide all\nshow cartoon, !the_rest\nshow surface, !the_rest\nset transparency, 0.1\nzoom\nscene F2, store\n\n") #only chain with surface
    pymol_script.write("hide all\nshow cartoon, !the_rest\nzoom\nscene F1, store\n\n") #only chain in cartoon
    pymol_script.write("set fog_start, 0\nset depth_cue, 0\n")#visual effects
    pymol_script.write('cmd.wizard("message", "Please us F1-F4 to switch between different scenes")')
    pymol_script.close()
    pdb_file.close()
    print_info()

create_pymol()
