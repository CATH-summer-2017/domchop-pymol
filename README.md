# DisplayRasmol.pl

We have an old internal CGI program that currently throws back a Rasmol script
that allows curators to view putative domain choppings in 3D.

It would be useful to update this script to throw back PyMOL compatible
commands as well (e.g. via an optional parameter).

The CGI script is included in this repo for reference, however it may not be 
possible to do much coding via GitHub since:

 * the script is part of our internal SVN repo
 * it has lots of dependencies on our local network (libraries, database connections, etc).
 
10gsA D2-78[A]+187-208[A] D79-186[A] F209-209[A]  
1a35A D236-319[A] D320-430[A] D431-580[A] D591-635[A]+713-764[A] F215-235[A] F581-590[A] F765-765[A]  
1a36A D2-215[A]+320-431[A] D232-319[A] D432-583[A] D584-765[A]  
4bgdA D451-471[A]+700-908[A] D472-699[A] D909-998[A] D999-1140[A] D1141-1198[A] D1199-1311[A] D1312-1540[A] D1541-1743[A]    D1744-1846[A] D1847-1989[A] D1990-2049[A] D2050-2163[A] F442-450  
1bvsA D1-65[A] D66-148[A] D149-199[A] F200-203[A]  
1cukA D1-66[A] D67-142[A] D156-203[A]  

 

