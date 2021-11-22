VENV = venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip

venv: $(VENV)/touchfile

venv/touchfile: requirements.txt
	python3 -m venv $(VENV)
	. venv/bin/activate; $(PIP) install -Ur requirements.txt
	touch venv/touchfile

clean:
	rm -rf $(VENV)
	find . -type f -name '*.pyc' -delete

	