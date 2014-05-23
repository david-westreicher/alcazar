import numpy as np
import subprocess
import sys

directions = [('R',[0,1]),('L',[0,-1]),('D',[1,0]),('U',[-1,0])]
class puzzle(object):
	def __init__(self,puzzlemap,width,height):
		print(str(width)+"x"+str(height)+" puzzle")
		self.width = width
		self.height = height
		self.puzzlemap = puzzlemap
		printPuzzle(puzzlemap)
	def __str__(self):
		return printPuzzle(self.puzzlemap,False)
	def getVal(self,i,j):
		return self.puzzlemap[j*2+1][i*2+1]
	def getNeighs(self,i,j):
		neighs = []
		realCoord = np.asarray([j*2+1,i*2+1])
		for d in directions:
			r = realCoord.copy()
			r += d[1]
			if(self.puzzlemap[r[0]][r[1]]==' '):
				#r += d[1]
				neighs.append((d[0],[r[1],r[0]]))
		return neighs

def printPuzzle(puzzlemap,printToo=True):
	string = ""
	if printToo:
		for line in puzzlemap:
			for el in line:
				print(el),
			print("\n"),
	else:
		for line in puzzlemap:
			for el in line:
				string+=el+" "
			string+="\n"
	return string
	
def read(filename):
	f = open(filename)
	lines = f.read().splitlines()
	puzzlemap = []
	width = 0
	height = 0
	verticalLine = True
	for line in lines:
		width = max(width,len(line))
		height+=1
		puzzlemap.append(list(line))
		verticalLine = not verticalLine
	f.close()
	width = width/2
	height = height/2
	return puzzle(puzzlemap,width,height)
	
def coordToVar(coord,puzzle):
	return coord[0]+coord[1]*(puzzle.width*2+1)
	
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
				variableCoordMap.append([0,0])
				megaclause.append(helperVar)
				allclauses.append([-helperVar,variables[i]])
				allclauses.append([-helperVar,variables[j]])
				for k in range(0,len(variables)):
					if(k!=i and k!=j):
						allclauses.append([-helperVar,-variables[k]])
		allclauses.append(megaclause)
		return allclauses

def encode(puzzle):
	clauses = []
	coordVariableMap = {}
	currentVariable = 1
	variableCoordMap = []
	exits = []
	for j,line in enumerate(puzzle.puzzlemap):
		for i,el in enumerate(line):
			if(el==" "):
				variableCoordMap.append([i,j])
				coordVariableMap[coordToVar([i,j],puzzle)] = currentVariable
				#print(([i,j],coordToVar([i,j],puzzle),currentVariable))
				if(j==0 or i==0 or j==len(puzzle.puzzlemap)-1 or i==len(puzzle.puzzlemap[0])-1):
					exits.append(currentVariable)
				currentVariable+=1
	#print(coordVariableMap)
	#print(variableCoordMap)
	#print(exits)
	#for every corner 2 lines need to be active
	for i in range(puzzle.width):
		for j in range(puzzle.height):
			#puzzle.puzzlemap[j*2+1][i*2+1] = lineSegmentsutf8[2]
			#print(((i,j),puzzle.getVal(i,j)))
			#print(((i,j),puzzle.getNeighs(i,j)))
			neighLineVars = [coordVariableMap[coordToVar(neigh[1],puzzle)] for neigh in puzzle.getNeighs(i,j)]
			for clause in exactlyTwo(neighLineVars,variableCoordMap):
				clauses.append(clause)
	
	#exactly two exits need to be active
	for clause in exactlyTwo(exits,variableCoordMap):
		clauses.append(clause)
	
	#print(puzzle)
	#print(clauses)
	#print([varToCoord(c[0],puzzle) for c in clauses])
	return clauses, variableCoordMap

def solve(clauses,variables):
	f = open("tmp.sat","w")
	f.write("p cnf "+str(len(variables))+" "+str(len(clauses))+"\n")
	for clause in clauses:
		for el in clause:
			f.write(str(el)+" ")
		f.write("0\n")
	f.close()
	subprocess.call(["minisat", "tmp.sat","out.ass"],stdout=subprocess.PIPE)
	f = open("out.ass")
	lines = f.read().splitlines()
	asss = [int(el) for el in lines[1].split(" ")]
	f.close()
	return asss[:-1]

def decode(puzzle,assignments,variables):
	for ass in assignments:
		index = abs(ass)-1
		coord = variables[index]
		#print(coord)
		if(ass>0):
			puzzle.puzzlemap[coord[1]][coord[0]] = '|' if coord[1]%2==0 else '-'

if __name__ == "__main__":
	puzzle = read(sys.argv[1])
	clauses,variables = encode(puzzle)
	assignments = solve(clauses,variables)
	decode(puzzle,assignments,variables)
	print("SOLUTION")
	print(puzzle)
