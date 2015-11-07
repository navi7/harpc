.PHONY: build dev dev_clean
default: build

BIN_PYTHON=python3
BIN_PIP=pip

build:
	pip install -r requirements.txt

dev:
	BIN_PIP=bin/pip3
	pyvenv build --copies --clear
	@ln -s build/bin bin
	@$(BIN_PIP) install -r requirements.txt

dev_clean:
	unlink bin
	rm -rf build/

