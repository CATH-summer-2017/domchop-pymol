# DisplayRasmol.pl

We have an old internal CGI program that currently throws back a Rasmol script
that allows curators to view putative domain choppings in 3D.

It would be useful to update this script to throw back PyMOL compatible
commands as well (e.g. via an optional parameter).

The CGI script is included in this repo for reference, however it may not be 
possible to do much coding via GitHub since:

 * the script is part of our internal SVN repo
 * it has lots of dependencies on our local network (libraries, database connections, etc).


 

