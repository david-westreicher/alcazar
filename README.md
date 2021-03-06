AlcaSAT
=========

An [alcazar] solver using SAT-techniques

Check out my [blog post](http://david-westreicher.github.io/2014/11/06/alcasat/) for more information.

Requirements
----
* python 2.7
* [pyside] and pyside-uic for the gui (the gui/gui.ui can be converted to the src/gui.py with ```pyside-uic gui/gui.ui > src/gui.py```)
* pyrcc4 to convert the *.qrc file to a resource.py file (```apt-get install pyqt4-dev-tools```) 
* [minisat] should be in your environment ```minisat test.dimacs```


What are SAT-techniques
-----------
Problems are encoded into [SAT]-formulas, which are then transformed into [CNF] and fed into a SAT-solver (in this case [minisat]).
The SAT-solver finds assignments, which lets the formula evaluate to TRUE. These assignments are then decoded into the original problem domain.
For more in-depth information check out my [blog post](http://david-westreicher.github.io/2014/11/06/alcasat/).

Usage
--------------


```
make
python src/alcazar.py samples/sample1.puzzle

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

![Video](https://david-westreicher.github.io/static/alcazar/demo.gif)

Puzzle-Format
-----------
```0``` represet corners, 
```space``` represent possible lines,
```x``` represent walls

TODO
-----------
* use threading to get instant feedback for big puzzles

Version
----

0.1

License
----

MIT


**Free Software, Hell Yeah!**

[minisat]:http://minisat.se
[pyside]:http://qt-project.org/wiki/pyside
[alcazar]:http://www.theincrediblecompany.com/alcazar-1/
[SAT]:http://en.wikipedia.org/wiki/Boolean_satisfiability_problem
[CNF]: http://en.wikipedia.org/wiki/Conjunctive_normal_form
