.PHONY: install run test clean

install:
	pip install pywin32 PyQt5 win10toast requests

run:
	python3 main_loop.py

test:
	python3 test_parser.py

clean:
	rm -rf __pycache__
	rm -f bugs.json
