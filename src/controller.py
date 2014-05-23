import gui
import random
import numpy as np
from PySide import QtCore, QtGui

class Example(QtGui.QWidget):
	def __init__(self,puzzle):
		super(Example, self).__init__()
		self.puzzle = puzzle
		self.CELL_SIZE = 50
		self.WALL_SIZE = 10
		self.SOLUTION_SIZE = 25
		self.mouseDown = False
	def paintEvent(self, event):
		qp = QtGui.QPainter()
		qp.begin(self)
		self.drawPuzzle(event, qp)
		qp.end()
	def mousePressEvent(self,event):
		self.mouseDown = True
		self.click(np.asarray([event.pos().x(),event.pos().y()]))
		self.update()
	def click(self,clickpos):
		translate = self.getTranslation()
		clickpos-=translate
		clickpos = (clickpos/self.CELL_SIZE)
		self.puzzle.puzzlemap[0][1] = ' '
		print(clickpos)
	def mouseReleaseEvent(self,event):
		self.mouseDown = False
	def mouseMoveEvent(self,event):
		pass
		#if(self.mouseDown):
		#	print(str(event.pos()))
	def getTranslation(self):
		size = self.size()
		maxsize = [self.puzzle.width*self.CELL_SIZE,self.puzzle.height*self.CELL_SIZE]
		translate = [(size.width()-maxsize[0])/2,(size.height()-maxsize[1])/2]
		return translate
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

class Model(object):
	def __init__(self,puzzle=None):
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
		widget = Example(self.model.puzzle)
		widget.setObjectName("widget")
		self.ui.horizontalLayout.removeWidget(self.ui.placeholder)
		self.ui.placeholder.setParent(None)
		sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(widget.sizePolicy().hasHeightForWidth())
		widget.setSizePolicy(sizePolicy)
		self.ui.horizontalLayout.insertWidget(0,widget)
		self.ui.horizontalLayout.setStretch(0, 4)
        
	def setupEvents(self):
		pass
		#self.ui.previewButton.clicked.connect(self.updateActiveCamTable)
		#self.ui.downloadButton.clicked.connect(self.download)
		
def startGUI(puzzle=None):
	app = QtGui.QApplication([])  
	controller = ControlMainWindow(Model(puzzle))
	controller.show()
	app.connect(app, QtCore.SIGNAL("lastWindowClosed()"),
			app, QtCore.SLOT("quit()"))
	app.exec_()
