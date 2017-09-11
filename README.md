# Display-pml.py
## Intro

The Display-pml script is designed to take the internal CATH chopping string as an input and produce a file of a .pml extension that will show the chopping of the chain.

## Main principle of the script

#### Inputs

The Display-pml script takes the string directly as an input from the website. 

The string looks like this: 
__*"10gs D2-78[A]+187-208[A] D79-186[A] F209-209[A]"*__. String has 3 main different "data-types":
* **10gs** - PDB ID of the protein.
* **D2-78[A]+187-208[A]** - coordinates of a domain. Different domains are separated by space, different pieces of a domain are linked by a plus sign
* **F209-209[A]** - coordinates of the fragments. Again, spaces separate the different fragments.

Another input is the config.ini file which allows the script to be compatible with both CATH and local PC, specifying the PATH to PDB files and their name format.

Lastly, the script also needs the pdb files for the proteins it is chopping.

#### Handling the information

The script takes all the inputs and the uses Regex to get information about the chopping (three main "data-types") and put it into more sensible form (dictionary for domains and list for fragments). 

A temporal file is created which will later be exported as a .pml file. Some important info added to it, like the proper colours etc. Then the pdb file is put into the new .pml file and then selection objects are created according to the chopping.

## How to use pml files

The pymol scripts the are produced can be very useful for DomChopping. They are opened using the pymol app, which is quite easy to install, with instructions for most Linux distros located [here](https://pymolwiki.org/index.php/Linux_Install) and for Windows [here](https://pymolwiki.org/index.php/Windows_Install). Once the system is configured to open .pml files with pymol DomChopping should be much easier.

## Useful tips for using Pymol

* use Ctrl+Shift and middle mouse button to zoom
* pressing buttons from F1 to F6 will toggle different scenes such as:
    1. Chain in cartoon
    1. Chain in cartoon with surface
    1. Chain in cartoon with the rest of the protein in ribbon
    1. Chain in cartoon with the whole protein's surface
    1. Chain in cartoon with the numerical labels of each Ca
    1. Whole protein with surface
 * tab on the right can be used to show/hide specific domains and change the view/colour/almost anything.
