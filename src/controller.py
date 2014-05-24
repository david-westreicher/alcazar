import gui
import newdialog
import random
import alcazar
import sys
import numpy as np
from PySide import QtCore, QtGui

class GameField(QtGui.QWidget):
	def __init__(self,puzzle):
		super(GameField, self).__init__()
		self.puzzle = puzzle
		self.CELL_SIZE = 50
		self.WALL_SIZE = 10
		self.SOLUTION_SIZE = 25
		self.mouseDown = False
		self.deleteActivated = True
		self.solvePuzzle()
		
	def paintEvent(self, event):
		qp = QtGui.QPainter()
		qp.begin(self)
		self.drawPuzzle(event, qp)
		qp.end()
	def mousePressEvent(self,event):
		self.mouseDown = True
		self.updateClick(np.asarray([event.pos().x(),event.pos().y()]))
	def mouseReleaseEvent(self,event):
		self.mouseDown = False
	def mouseMoveEvent(self,event):
		if(self.mouseDown):
			self.updateClick(np.asarray([event.pos().x(),event.pos().y()]))
			
	def updateClick(self,clickpos):
		def flip(x,y):
			if(x<len(self.puzzle.puzzlemap) and y<len(self.puzzle.puzzlemap[0])):
				val = self.puzzle.puzzlemap[x][y]
				self.puzzle.puzzlemap[x][y] = ' ' if self.deleteActivated else 'x'
				return True
			return False
		clickpos =(clickpos-self.getTranslation())/float(self.CELL_SIZE)+0.2
		change = False
		intcolumn = int(clickpos[0])
		column = clickpos[0]-intcolumn
		introw = int(clickpos[1])
		row = clickpos[1]-introw
		if(introw>=0 and introw<=self.puzzle.height and intcolumn>=0 and intcolumn<=self.puzzle.width):
			#horizontal
			if(row<0.5 and column>0.5):
				change = flip(introw*2,intcolumn*2+1)
			#vertical
			if(column<0.5 and row>0.5):
				change = flip(introw*2+1,intcolumn*2)
		if change:
			self.solvePuzzle()
	def getTranslation(self):
		size = self.size()
		maxsize = [self.puzzle.width*self.CELL_SIZE,self.puzzle.height*self.CELL_SIZE]
		translate = [(size.width()-maxsize[0])/2,(size.height()-maxsize[1])/2]
		return translate
		
	def solvePuzzle(self):
		try:
			alcazar.solvePuzzle(self.puzzle)
		except:
			#print("Can't solve this puzzle")
			#print "Unexpected error:", [el for el in sys.exc_info()]
			self.puzzle.clearSolution()
		self.update()
	def setPuzzle(self, newpuzzle):
		self.puzzle = newpuzzle
		self.solvePuzzle()
		
	def drawPuzzle(self, event, qp):
		qp.setPen(QtCore.Qt.black)
		translate = self.getTranslation()
		#draw grid
		for i in range(self.puzzle.width+1):
			for j in range(self.puzzle.height+1):
				x1 = 0
				y1 = j*self.CELL_SIZE
				x2 = (self.puzzle.width)*self.CELL_SIZE
				y2 = j*self.CELL_SIZE
				x1+=translate[0]
				y1+=translate[1]
				x2+=translate[0]
				y2+=translate[1]
				qp.drawLine(QtCore.QPoint(x1,y1),QtCore.QPoint(x2,y2))
				x1 = i*self.CELL_SIZE
				y1 = 0
				x2 = i*self.CELL_SIZE
				y2 = (self.puzzle.height)*self.CELL_SIZE
				x1+=translate[0]
				y1+=translate[1]
				x2+=translate[0]
				y2+=translate[1]
				qp.drawLine(QtCore.QPoint(x1,y1),QtCore.QPoint(x2,y2))
		#draw walls
		for j,line in enumerate(self.puzzle.puzzlemap):
			for i,el in enumerate(line):
				if(el=='x'):
					#horizontal
					if(j%2==0 and i%2==1):
						x = (i-1)*self.CELL_SIZE/2-self.WALL_SIZE/2
						y = j*self.CELL_SIZE/2-self.WALL_SIZE/2
						x+=translate[0]
						y+=translate[1]
						qp.fillRect(x,y,self.CELL_SIZE+self.WALL_SIZE,self.WALL_SIZE,QtCore.Qt.black)
					#vertical
					if(j%2==1):
						x = i*self.CELL_SIZE/2-self.WALL_SIZE/2
						y = (j-1)*self.CELL_SIZE/2-self.WALL_SIZE/2
						x+=translate[0]
						y+=translate[1]
						qp.fillRect(x,y,self.WALL_SIZE,self.CELL_SIZE+self.WALL_SIZE,QtCore.Qt.black)
		#draw solution
		for j,line in enumerate(self.puzzle.puzzlemap):
			for i,el in enumerate(line):
				if(el=='-'):
					#horizontal
					x = (i-1)*self.CELL_SIZE/2-self.SOLUTION_SIZE/2
					y = j*self.CELL_SIZE/2-self.SOLUTION_SIZE/2
					x+=translate[0]
					y+=translate[1]
					qp.fillRect(x,y,self.CELL_SIZE+self.SOLUTION_SIZE,self.SOLUTION_SIZE,QtCore.Qt.red)
				if(el=='|'):
					#vertical
					x = i*self.CELL_SIZE/2-self.SOLUTION_SIZE/2
					y = (j-1)*self.CELL_SIZE/2
					x+=translate[0]
					y+=translate[1]
					qp.fillRect(x,y,self.SOLUTION_SIZE,self.CELL_SIZE,QtCore.Qt.red)

	
def generateEmptyPuzzle(sizes):
	puzzle = alcazar.puzzle([[' ' for i in range(sizes[0]*2+1)] for j in range(sizes[1]*2+1)],sizes[0],sizes[1])
	for j,line in enumerate(puzzle.puzzlemap):
		for i,el in enumerate(line):
			if(j%2==1 and i%2==1):
				puzzle.puzzlemap[j][i]='0'
			if(j%2==0 and i%2==0):
				puzzle.puzzlemap[j][i]='x'
	return puzzle

class Model(object):
	def __init__(self,puzzle=None, sizes=(3,3)):
		if(puzzle is None):
			puzzle = generateEmptyPuzzle(sizes)
		self.puzzle = puzzle

class ControlMainWindow(QtGui.QMainWindow):
	def __init__(self, model, parent=None):
		super(ControlMainWindow, self).__init__(parent)
		self.model = model
		self.ui = gui.Ui_MainWindow()
		self.ui.setupUi(self)
		self.addDrawingRect()
		self.setupEvents()

	def addDrawingRect(self):
		gf = GameField(self.model.puzzle)
		gf.setObjectName("gf")
		self.ui.horizontalLayout.removeWidget(self.ui.placeholder)
		self.ui.placeholder.setParent(None)
		sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(gf.sizePolicy().hasHeightForWidth())
		gf.setSizePolicy(sizePolicy)
		self.ui.horizontalLayout.insertWidget(0,gf)
		self.ui.horizontalLayout.setStretch(0, 4)
		self.gamefield = gf

	def addremoveline(self):
		self.gamefield.deleteActivated = not self.gamefield.deleteActivated
	def openFile(self):
		dialog = QtGui.QFileDialog(self)
		dialog.setFileMode(QtGui.QFileDialog.AnyFile)
		if dialog.exec_():
			filename = str(dialog.selectedFiles()[0])
			newpuzzle = alcazar.read(filename)
			self.gamefield.setPuzzle(newpuzzle)
	def newPuzzle(self):
		dialog =  QtGui.QDialog(self)
		myDialog = newdialog.Ui_Dialog()
		myDialog.setupUi(dialog)
		if dialog.exec_():
			width = myDialog.width.value()
			height = myDialog.height.value()
			newpuzzle = generateEmptyPuzzle((width,height))
			self.gamefield.setPuzzle(newpuzzle)
	def savePuzzle(self):
		dialog = QtGui.QFileDialog(self)
		dialog.setFileMode(QtGui.QFileDialog.AnyFile)
		if dialog.exec_():
			filename = str(dialog.selectedFiles()[0])
			f = open(filename,'w')
			for line in self.gamefield.puzzle.puzzlemap:
				newline = ''.join(line)
				f.write(newline+"\n")
			f.close()
			print("saving to "+filename)
		
	def setupEvents(self):
		self.ui.actionAddRemoveLines.triggered.connect(self.addremoveline)
		self.ui.action_Open.triggered.connect(self.openFile)
		self.ui.actionNew.triggered.connect(self.newPuzzle)
		self.ui.actionSave.triggered.connect(self.savePuzzle)
		
def startGUI(puzzle=None):
	app = QtGui.QApplication([])  
	controller = ControlMainWindow(Model(puzzle))
	controller.show()
	app.connect(app, QtCore.SIGNAL("lastWindowClosed()"),
			app, QtCore.SLOT("quit()"))
	app.exec_()
