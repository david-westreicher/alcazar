PYSIDEUIC = pyside-uic
PYRCC = pyrcc4
RESOURCES = gui/resources.qrc
SOURCES = src/gui.py src/resources_rc.py src/newdialog.py
PYCS = $(SOURCES:.py=.pyc)
UIPYS = src/gui.py src/newdialog.py

src/%.py: gui/%.ui
	$(PYSIDEUIC) $< -o $@

all: $(UIPYS)
	$(PYRCC) $(RESOURCES) -o src/resources_rc.py
 
clean:
	-rm -f $(SOURCES)
	-rm -f $(PYCS)
