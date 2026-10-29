.PHONY: install run run-mud test clean help build sync-upstream

PYTHON := python3.13
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
	@echo "  make sync-upstream - Merge upstream LlamaTale into our fork's hallow-mud branch"

install:
	git submodule update --init
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV)
	@echo "Installing LlamaTale dependencies..."
	$(VENV_BIN)/pip install --upgrade pip
	$(VENV_BIN)/pip install -r LlamaTale/requirements.txt
	# setuptools provides distutils, which tale imports and Python 3.12+ removed
	$(VENV_BIN)/pip install -r LlamaTale/requirements_dev.txt pytest setuptools
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
	# tests use paths relative to LlamaTale; remove the files they leave behind
	cd $(LLAMATALE) && $(PWD)/$(VENV_BIN)/python -m pytest tests -q; status=$$?; \
		rm -f world.json story_config.json tests/files/test_name.jpg tests/files/test_name2.jpg; exit $$status

clean:
	rm -rf $(VENV) __pycache__ LlamaTale/build LlamaTale/dist LlamaTale/*.egg-info
	@echo "Cleaned!"

sync-upstream:
	cd LlamaTale && (git remote get-url neph1 >/dev/null 2>&1 || git remote add neph1 https://github.com/neph1/LlamaTale.git) \
		&& git fetch neph1 && git checkout hallow-mud && git merge --no-edit neph1/master && git push origin hallow-mud
	git add LlamaTale
	@echo "LlamaTale synced with upstream; commit the updated submodule pointer."
