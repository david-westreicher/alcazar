alcazar-SAT
=========

An [alcazar] solver using SAT-techniques

Requirements
----
* python 2.7
* [minisat] should be in your environment ```minisat test.dimacs```


What are SAT-techniques
-----------
Problems are encoded into [SAT]-formulas, which are then transformed into [CNF] and fed into a SAT-solver (in this case [minisat]).
The SAT-solver finds assignments, which lets the formula evaluate to TRUE. These assignments are then decoded into the original problem domain.

Usage
--------------

```
python alcazar.py samples/sample1.puzzle

3x4 puzzle
x x x x x x x 
x 0   0   0 x 
x   x x x   x 
  0 x 0   0 x 
x   x   x   x 
  0 x 0   0 x 
x   x x x   x 
x 0   0   0 X 
x x x x x x x 
SOLUTION
x x x x x x x 
x 0 - 0 - 0 x 
x | x x x | x 
- 0 x 0 - 0 x 
x   x | x   x 
- 0 x 0 - 0 x 
x | x x x | x 
x 0 - 0 - 0 x 
x x x x x x x 


```

Puzzle-Format
-----------
```0``` represet corners, 
```space``` represent possible lines,
```x``` represent walls

TODO
-----------
* fix one loop problem (find loops and add the negated form to the formula)
* helper variables should be handled nicer
* show error if formula UNSAT
* gui

Version
----

0.1

License
----

MIT


**Free Software, Hell Yeah!**

[minisat]:http://minisat.se
[alcazar]:http://www.theincrediblecompany.com/alcazar-1/
[SAT]:http://en.wikipedia.org/wiki/Boolean_satisfiability_problem
[CNF]: http://en.wikipedia.org/wiki/Conjunctive_normal_form
