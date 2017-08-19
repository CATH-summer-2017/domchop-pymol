#!/usr/bin/python3
print("Content-type: text/x pymol")
import re

the_string = '''
4bgdA D451-471[A]+700-908[A] D472-699[A] D909-998[A] D999-1140[A] D1141-1198[A] D1199-1311[A] D1312-1540[A] D1541-1743[A] D1744-1846[A] D1847-1989[A] D1990-2049[A] D2050-2163[A] F442-450
'''

pdb_dir = '/home/ilsenatorov/domchop-pymol/pdb_files/'
pml_dir = '/home/ilsenatorov/domchop-pymol/created_scripts/'
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

#puts colours from CATH
def set_colours():
    for colour in norm_colours:
        print("\nset_colour dom" + str(norm_colours.index(colour) + 1) + ", " + colour)

#puts pdb info into the  file
def fetch_pdb(pdb, pdb_id):#
    print('\ncmd.read_pdbstr("""\\' + '\n')
    for line in pdb: #takes each line of pdb and adds it to the  with a backslash at the end
        print(line.rstrip("\n") + "\\\n")
    print('""", "' + pdb_id + '")\n')

#creates selection of each domain in
def add_domains(source_of_domains):
    count = 1
    number_of_doms = len(fetch_domains(source_of_domains))
    for domain in range(number_of_doms):
        print("select " + pdb_id_chain + str(count).zfill(2) + ",", end='')
        for coordin in fetch_domains(source_of_domains)[pdb_id_chain + str(count).zfill(2)]:
            if coordin == fetch_domains(source_of_domains)[pdb_id_chain + str(count).zfill(2)][-1]:
                print(" chain " + pdb_id_chain[-1] + " and resi " + coordin)
                break
            print(" chain " + pdb_id_chain[-1] + " and resi " + coordin + " +")
        count += 1
        print("\n")

#puts fragment selection in the
def add_fragments(source_of_fragments):
    print("\nselect fragments, " + "chain " + pdb_id_chain[-1] + " and ", end='')
    if len(fetch_fragments(source_of_fragments)) == 0:
        return
    for fragment in fetch_fragments(source_of_fragments):  # puts all fragments in ., creating one object for them
        if fragment == fetch_fragments(source_of_fragments)[-1]:  # doesn't add a + if it is the last fragment
            print("resi " + fragment + "\n")
            break
        print("resi " + str(fragment) + " + ")

#colours the domains according to the chopping
def colour_domains(source_of_domains):
    number_of_doms = len(fetch_domains(source_of_domains))
    count = 1
    for domain in range(number_of_doms):  # colours the domains
        print("colour dom" + str(count) + ", " + pdb_id_chain + str(count).zfill(2) + "\n")
        count += 1

#gets info about the chopped chain
def print_info():
    print("Chain ID = " + pdb_id_chain)
    print("Number of domains = " + str(len(fetch_domains(domains))))
    print("Domains: ")
    print(fetch_domains(domains))
    print("Fragments list: ")
    print(fetch_fragments(fragments))

def create_pymol(): #compiles data into the  file
    pdb_file = open(pdb_dir + pdb_id_chain[0:4] + '.pdb', 'r') #opens a pdb file for the protein
    set_colours()
    fetch_pdb(pdb_file, pdb_id_chain[0:4])
    add_domains(domains)
    add_fragments(fragments)
    print("\nselect the_rest, not chain " + pdb_id_chain[-1]) #creates the rest of the protein as an object
    print("\n\n")
    colour_domains(domains)
    print("\ncolour White, fragments") #colours the fragments
    print("\nspectrum count, rainbow, the_rest")#colours the rest of the chain
    print("\nhide all\ndeselect\ndelete sele\n\n")#creates blank screen
    print("hide all\nshow surface, all\nshow cartoon, all\nset transparency, 0.1\nzoom\nscene F4, store\n\n")#all of protein with surface
    print("hide all\nshow cartoon, !the_rest\nshow ribbon, the_rest\nzoom\nscene F3, store\n\n")#all of protein in cartoon
    print("hide all\nshow cartoon, !the_rest\nshow surface, !the_rest\nset transparency, 0.1\nzoom\nscene F2, store\n\n") #only chain with surface
    print("hide all\nshow cartoon, !the_rest\nzoom\nscene F1, store\n\n") #only chain in cartoon
    print("set fog_start, 0\nset depth_cue, 0\n")#visual effects
    print('cmd.wizard("message", "Please us F1-F4 to switch between different scenes")')
    pdb_file.close()



create_pymol()
