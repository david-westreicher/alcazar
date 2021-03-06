import numpy as np
import subprocess
import sys
import os
import time
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
			cellVal = self.puzzlemap[r[0]][r[1]]
			if(cellVal==' ' or cellVal=='|' or cellVal=='-'):
				neighs.append((d[0],[r[1],r[0]]))
		return neighs
	def clearSolution(self):
		for j,line in enumerate(self.puzzlemap):
			for i,el in enumerate(line):
				if(el=="|" or el=="-"):
					self.puzzlemap[j][i] = ' '

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
	
def coordToVar(coord,puzzle):
	return coord[0]+coord[1]*(puzzle.width*2+1)
	
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
		
	clauses = []
	coordVariableMap = {}
	currentVariable = 1
	variableCoordMap = []
	exits = []
	#build variable to coord maps and find exits
	for j,line in enumerate(puzzle.puzzlemap):
		for i,el in enumerate(line):
			if(el==" " or el=="|" or el=="-"):
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
		
	return clauses, variableCoordMap, coordVariableMap

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
		if(type(coord) is list):
			if ass>0:
				puzzle.puzzlemap[coord[1]][coord[0]] = '|' if coord[1]%2==0 else '-'
			else:
				puzzle.puzzlemap[coord[1]][coord[0]] = ' '

def findLoops(puzzle):
	def findLoopStart(puzzle,bitmask):
		for i in range(puzzle.width*2+1):
			for j in range(puzzle.height*2+1):
				val = puzzle.puzzlemap[j][i]
				if((not bitmask[i][j]) and (val=='-' or val=='|')):
					return np.asarray([i,j])
	def getNext(start,puzzle,bitmask):
		for (_,d) in directions:
			tmp = start+d
			if(tmp[0]>=0 and tmp[0]<puzzle.width*2+1 and tmp[1]>=0 and tmp[1]<puzzle.height*2+1):
				val = puzzle.puzzlemap[tmp[1]][tmp[0]]
				if((not bitmask[tmp[0]][tmp[1]]) and (val=='0' or val=='-' or val=='|')):
					return tmp
		return None
	loops = []
	bitmask = [[False for i in range(puzzle.height*2+1)] for j in range(puzzle.width*2+1)]
	while(True):
		path = []
		current = findLoopStart(puzzle,bitmask)
		if(current is None):
			break
		path.append(current)
		bitmask[current[0]][current[1]]=True
		while(True):
			current = getNext(current,puzzle,bitmask)
			if(current is None):
				break
			else:
				bitmask[current[0]][current[1]]=True
				path.append(current)
		#check if loop (path ends not on border)
		if(path[-1][0]>0 and path[-1][1]>0 and path[-1][0]<puzzle.width*2 and path[-1][1]<puzzle.height*2):
			loops.append([el for i,el in enumerate(path) if i%2==0])
	return loops

def solvePuzzle(puzzle):
	clauses,variables,coordVariableMap = encode(puzzle)
	assignments = solve(clauses,len(variables))
	decode(puzzle,assignments,variables)
	hasLoops = True
	iterations = 0
	startTime = time.time()
	while(hasLoops):
		iterations+=1
		loops = findLoops(puzzle)
		if(len(loops)==0):
			hasLoops = False
		else:
			for loop in loops:
				clauses.append([-coordVariableMap[coordToVar(el,puzzle)] for el in loop])
			assignments = solve(clauses,len(variables))
			decode(puzzle,assignments,variables)
	print iterations," iterations with hybrid solver ",(time.time()-startTime)," sec"

if __name__ == "__main__":
	if(len(sys.argv)>1):
		puzzle = read(sys.argv[1])
		print(puzzle)
		solvePuzzle(puzzle)
		print("SOLUTION")
		print(puzzle)
	else:
		controller.startGUI()
		
