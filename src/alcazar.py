import numpy as np
import subprocess
import sys
import os
import tempfile
import controller

directions = [('R',[0,1]),('L',[0,-1]),('D',[1,0]),('U',[-1,0])]
class puzzle(object):
	def __init__(self,puzzlemap,width,height):
		print(str(width)+"x"+str(height)+" puzzle")
		self.width = width
		self.height = height
		self.puzzlemap = puzzlemap
	def __str__(self):
		string = ""
		for line in self.puzzlemap:
			for el in line:
				string+=el+" "
			string+="\n"
		return string
	def getNeighs(self,i,j):
		neighs = []
		realCoord = np.asarray([j*2+1,i*2+1])
		for d in directions:
			r = realCoord.copy()
			r += d[1]
			if(self.puzzlemap[r[0]][r[1]]==' '):
				neighs.append((d[0],[r[1],r[0]]))
		return neighs

# *.puzzle -> puzzle object
def read(filename):
	f = open(filename)
	lines = f.read().splitlines()
	puzzlemap = []
	width = 0
	height = 0
	for line in lines:
		width = max(width,len(line))
		height+=1
		puzzlemap.append(list(line))
	f.close()
	width = width/2
	height = height/2
	return puzzle(puzzlemap,width,height)
	
# puzzle object -> boolean clauses
def encode(puzzle):
	'''
    exactlyTwo({x_1, ... , x_n}) = 

    \  /                /\
     \/   (x_i /\ x_j  /  \  -x_k ) = 
     i<j              k!=i,j
	 
     \  /                              /\
     (\/ a_l) /\ (a_l -> (x_i /\ x_j  /  \  -x_k ) = 
                                     k!=i,j
	 	 				 			  
     \  /                                         /\
     (\/ a_l) /\ (-a_l \/ x_i) /\ (-a_l \/ x_j)  /  \  (-a_l \/ -x_k) ) 
                                                k!=i,j
	'''
	#encoding of the exactly two constraint (converted to CNF with Wilson transform)
	def exactlyTwo(variables,variableCoordMap):
		variablesNum = len(variables)
		if variablesNum<2:
			raise NameError('Two few variables')
		elif variablesNum==2:
			return [[variables[0]],[variables[1]]]
		else:
			allclauses = []
			megaclause = []
			for i in range(0,len(variables)-1):
				for j in range(i+1,len(variables)):
					helperVar = len(variableCoordMap)+1
					variableCoordMap.append('helpervar'+str(helperVar))
					megaclause.append(helperVar)
					allclauses.append([-helperVar,variables[i]])
					allclauses.append([-helperVar,variables[j]])
					for k in range(0,len(variables)):
						if(k!=i and k!=j):
							allclauses.append([-helperVar,-variables[k]])
			allclauses.append(megaclause)
			return allclauses
			
	def coordToVar(coord,puzzle):
		return coord[0]+coord[1]*(puzzle.width*2+1)
		
	clauses = []
	coordVariableMap = {}
	currentVariable = 1
	variableCoordMap = []
	exits = []
	#build variable to coord maps and find exits
	for j,line in enumerate(puzzle.puzzlemap):
		for i,el in enumerate(line):
			if(el==" "):
				variableCoordMap.append([i,j])
				coordVariableMap[coordToVar([i,j],puzzle)] = currentVariable
				if(j==0 or i==0 or j==len(puzzle.puzzlemap)-1 or i==len(puzzle.puzzlemap[0])-1):
					exits.append(currentVariable)
				currentVariable+=1
				
	#for every corner 2 lines need to be active
	for i in range(puzzle.width):
		for j in range(puzzle.height):
			neighLineVars = [coordVariableMap[coordToVar(neigh[1],puzzle)] for neigh in puzzle.getNeighs(i,j)]
			for clause in exactlyTwo(neighLineVars,variableCoordMap):
				clauses.append(clause)
	
	#exactly two exits need to be active
	for clause in exactlyTwo(exits,variableCoordMap):
		clauses.append(clause)
		
	return clauses, variableCoordMap

# boolean clauses -> assignment
def solve(clauses,variablenum):
	f = tempfile.NamedTemporaryFile(mode = "w", delete = False)
	f.write("p cnf "+str(variablenum)+" "+str(len(clauses))+"\n")
	for clause in clauses:
		for el in clause:
			f.write(str(el)+" ")
		f.write("0\n")
	f.close()
	f2 = tempfile.NamedTemporaryFile(mode = "r")
	subprocess.call(["minisat", f.name,f2.name],stdout=subprocess.PIPE)
	lines = f2.read().splitlines()
	asss = [int(el) for el in lines[1].split(" ")]
	f2.close()
	os.remove(f.name)
	return asss[:-1]

#assignment -> solved puzzle
def decode(puzzle,assignments,variables):
	for ass in assignments:
		index = abs(ass)-1
		coord = variables[index]
		if(type(coord) is list and ass>0):
			puzzle.puzzlemap[coord[1]][coord[0]] = '|' if coord[1]%2==0 else '-'

if __name__ == "__main__":
	puzzle = read(sys.argv[1])
	print(puzzle)
	clauses,variables = encode(puzzle)
	assignments = solve(clauses,len(variables))
	decode(puzzle,assignments,variables)
	print("SOLUTION")
	print(puzzle)
	controller.startGUI(puzzle)
