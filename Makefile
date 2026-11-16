PYTHON = python

.PHONY: run test demo clean

run:
	$(PYTHON) -m src.emulator

test:
	$(PYTHON) -m unittest discover -s tests

demo:
	cmd /c scripts\test_all_params.bat

clean:
	$(PYTHON) -c "[__import__('shutil').rmtree(p, ignore_errors=True) \
		for p in __import__('pathlib').Path('.').rglob('__pycache__')]"
