SHELL = /bin/sh
PYSIDEUIC = pyside-uic
PYRCC = pyrcc4
UIS = gui/gui.ui
RESOURCES = gui/resources.qrc
SOURCES = src/gui.py src/resources_rc.py
PYCS = $(SOURCES:.py=.pyc)
 
all:
	$(PYSIDEUIC) $(UIS) -o src/gui.py
	$(PYRCC) $(RESOURCES) -o src/resources_rc.py
 
clean:
	-rm -f $(SOURCES)
	-rm -f $(PYCS)
