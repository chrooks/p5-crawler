venv: venv/bin/activate

venv/bin/activate: requirements.txt
	python3 -m venv venv
	./venv/bin/pip install -r requirements.txt

clean:
	rm -rf venv
	find . -type f -name '*.pyc' -delete