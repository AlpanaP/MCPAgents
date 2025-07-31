# BusinessLicenseNavigator Makefile
# =================================

.PHONY: help install install-dev clean test lint format type-check run run-web build docs clean-cache

# Default target
help: ## Show this help message
	@echo "BusinessLicenseNavigator - AI-Powered License Guidance System"
	@echo "=========================================================="
	@echo ""
	@echo "Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation
install: ## Install production dependencies
	pip install -e .

install-dev: ## Install development dependencies
	pip install -e ".[dev]"

# Development
run: ## Run the chat interface
	python main.py

run-web: ## Run the web interface (if available)
	python main.py web

test: ## Run all tests
	pytest tests/ -v

test-coverage: ## Run tests with coverage
	pytest tests/ --cov=src --cov-report=html --cov-report=term

lint: ## Run linting checks
	flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503

format: ## Format code with black
	black src/ tests/ --line-length=88

format-check: ## Check if code is formatted correctly
	black src/ tests/ --line-length=88 --check

type-check: ## Run type checking with mypy
	mypy src/ --ignore-missing-imports

# Code Quality
quality: format lint type-check ## Run all code quality checks

# Building and Packaging
build: ## Build the package
	python -m build

clean: ## Clean build artifacts and cache
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true

clean-cache: ## Clean Python cache files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true

# Documentation
docs: ## Generate documentation
	@echo "Documentation is in markdowns/ directory"
	@echo "Available docs:"
	@ls -la markdowns/

# State Management
add-state: ## Add a new state (usage: make add-state STATE=CA NAME="California")
	@if [ -z "$(STATE)" ] || [ -z "$(NAME)" ]; then \
		echo "Usage: make add-state STATE=CA NAME=\"California\""; \
		exit 1; \
	fi
	python src/add_new_state.py --state $(STATE) --name "$(NAME)"

test-state: ## Test state structure
	python tests/test_state_structure.py

# Development Workflow
dev-setup: install-dev ## Set up development environment
	@echo "Development environment setup complete!"
	@echo "Run 'make run' to start the application"

dev: quality test ## Run development checks (format, lint, type-check, test)

# Docker (if needed in future)
docker-build: ## Build Docker image
	docker build -t businesslicensenavigator .

docker-run: ## Run Docker container
	docker run -p 8000:8000 businesslicensenavigator

# Database and Services
setup-qdrant: ## Setup Qdrant vector database
	@echo "Setting up Qdrant vector database..."
	@echo "Note: This requires Qdrant to be installed and running"

# Configuration
check-config: ## Check configuration files
	@echo "Checking configuration files..."
	@ls -la src/config/
	@echo ""
	@echo "Configuration files found:"
	@find src/config/ -name "*.json" -exec basename {} \;

# Monitoring and Logs
logs: ## Show application logs
	@echo "Application logs would be displayed here"
	@echo "Add logging configuration to see actual logs"

# Security
security-check: ## Run security checks
	@echo "Running security checks..."
	@echo "Consider using bandit for security analysis: pip install bandit"
	@echo "bandit -r src/"

# Performance
profile: ## Profile the application
	@echo "Profiling tools:"
	@echo "- cProfile: python -m cProfile -o profile.prof main.py"
	@echo "- memory_profiler: pip install memory_profiler"
	@echo "- line_profiler: pip install line_profiler"

# Backup and Restore
backup: ## Backup configuration and data
	@echo "Creating backup..."
	tar -czf backup-$(shell date +%Y%m%d-%H%M%S).tar.gz src/ tests/ markdowns/

restore: ## Restore from backup (usage: make restore BACKUP=backup-20240101-120000.tar.gz)
	@if [ -z "$(BACKUP)" ]; then \
		echo "Usage: make restore BACKUP=backup-filename.tar.gz"; \
		exit 1; \
	fi
	@echo "Restoring from $(BACKUP)..."
	tar -xzf $(BACKUP)

# Git helpers
git-status: ## Show git status
	git status

git-clean: ## Clean untracked files
	git clean -fd

# Project Information
info: ## Show project information
	@echo "BusinessLicenseNavigator Project Information"
	@echo "=========================================="
	@echo "Version: $(shell python -c "import src; print(src.__version__)" 2>/dev/null || echo "Unknown")"
	@echo "Python: $(shell python --version)"
	@echo "Location: $(shell pwd)"
	@echo ""
	@echo "Source files: $(shell find src/ -name '*.py' | wc -l)"
	@echo "Test files: $(shell find tests/ -name '*.py' | wc -l)"
	@echo "Config files: $(shell find src/config/ -name '*.json' | wc -l)"

# Default target
.DEFAULT_GOAL := help 