PYC = pyinstaller
WORKPATH = ./build
DISTPATH = ./dist
PYCOPTIONS = --noconsole --onefile --icon icon.ico --workpath $(WORKPATH) --distpath $(DISTPATH)
TARGET = LangtonAnt.py

all :
	@echo ".......... Building .py to executable..."
	$(PYC) $(PYCOPTIONS) $(TARGET)
	@echo "   "
	@echo ".......... Copying the resources to the distpath..."
	cp icon.ico $(DISTPATH)/icon.ico
	cp ant.png $(DISTPATH)/ant.png
	@echo "   "
	@echo ".......... Done!"

clean:
	rm -rf $(WORKPATH)
	rm -rf $(DISTPATH)
	rm -f LangtonAnt.spec
