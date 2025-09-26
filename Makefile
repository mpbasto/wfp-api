VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

# For Windows
ifeq ($(OS), Windows_NT)
	PYTHON = $(VENV)\Scripts\python.exe
	PIP = $(VENV)\Scripts\pip.exe
	ACTIVATE = $(VENV)\Scripts\activate
else
    ACTIVATE = source $(VENV)/bin/activate
endif

.PHONY: all venv install activate

all: venv install

# Create virtual environment if it doesn't exist
venv:
	@if [ ! -d "$(VENV)" ]; then \
		echo "Creating virtual environment..."; \
		python -m venv $(VENV); \
	else \
		echo "Virtual environment already exists."; \
	fi

# Install dependencies from requirements.txt
install: venv
	@echo "Installing dependencies..."
	@$(PIP) install --upgrade pip
	@$(PIP) install -r requirements.txt

# Print command to activate venv
activate:
	@echo "Run the following command to activate the virtual environment:"
	@echo "$(ACTIVATE)"

# Open psql in Docker container
psql:
	@docker exec -it wfp_postgres psql -U wfp_user -d wfp_db