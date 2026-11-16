PYTHON = python

run:
	$(PYTHON) src/emulator.py

test:
	$(PYTHON) -m unittest discover -s tests

clean:
	$(PYTHON) -c "import shutil, pathlib; 
	\[shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]"