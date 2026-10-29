.PHONY: install run run-mud test clean help build

PYTHON := python3
VENV := venv
VENV_BIN := $(VENV)/bin
LLAMATALE := $(PWD)/LlamaTale

help:
	@echo "Hallow Mud - Makefile"
	@echo "Available targets:"
	@echo "  make install    - Install dependencies in virtual environment"
	@echo "  make run        - Run in interactive fiction (IF) mode"
	@echo "  make run-mud    - Run in MUD server mode"
	@echo "  make test       - Run tests"
	@echo "  make clean      - Remove virtual environment and build artifacts"
	@echo "  make build      - Build the package"

install:
	git submodule update --init
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV)
	@echo "Installing LlamaTale dependencies..."
	$(VENV_BIN)/pip install --upgrade pip
	$(VENV_BIN)/pip install -r LlamaTale/requirements.txt
	$(VENV_BIN)/pip install -e LlamaTale
	@echo "Installation complete!"

run:
	@if [ ! -f $(VENV_BIN)/python ]; then \
		echo "Virtual environment not found. Run 'make install' first."; \
		exit 1; \
	fi
	cd $(LLAMATALE) && PYTHONPATH=$(LLAMATALE) $(PWD)/$(VENV_BIN)/python -m tale.main --game $(PWD)/story --mode if

run-mud:
	@if [ ! -f $(VENV_BIN)/python ]; then \
		echo "Virtual environment not found. Run 'make install' first."; \
		exit 1; \
	fi
	cd $(LLAMATALE) && PYTHONPATH=$(LLAMATALE) $(PWD)/$(VENV_BIN)/python -m tale.main --game $(PWD)/story --mode mud

build:
	@echo "Building..."
	@if [ ! -f $(VENV_BIN)/python ]; then \
		echo "Virtual environment not found. Run 'make install' first."; \
		exit 1; \
	fi
	$(VENV_BIN)/pip install -e LlamaTale
	@echo "Build complete!"

test:
	@if [ ! -f $(VENV_BIN)/python ]; then \
		echo "Virtual environment not found. Run 'make install' first."; \
		exit 1; \
	fi
	$(VENV_BIN)/python -m pytest LlamaTale/tests/ -v 2>&1 | tail -30

clean:
	rm -rf $(VENV) __pycache__ LlamaTale/build LlamaTale/dist LlamaTale/*.egg-info
	@echo "Cleaned!"
