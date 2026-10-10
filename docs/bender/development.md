# Development Setup

This document describes how to set up the independent Python development environment for Bender.

## Supported Python Version
Bender requires Python >= 3.12.

## Creating a Virtual Environment
It is recommended to use a clean virtual environment for development:
```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

## Installing Bender in Development Mode
You can install Bender directly from the source tree in development mode, which includes locked development dependencies (pytest, pytest-cov, ruff, and build):
```bash
pip install -e ".[dev]"
```

Or you can use the generated `requirements-dev.txt` for an exact reproducible environment:
```bash
pip install -r requirements-dev.txt
pip install -e .
```

## Running Tests and Code Quality Checks
To execute the test suite without altering mathematical expected values:
```bash
python -m pytest -q
```

To run the linter and format checker:
```bash
python -m ruff check .
```

To verify dependencies and environment consistency:
```bash
python -m pip check
```

## Building Distribution Artifacts
To produce a valid wheel (`.whl`) and source distribution (`.tar.gz`):
```bash
python -m build
```
Artifacts will be available in the `dist/` directory.

## Current Limitations
- The project is currently a foundational layout (BND-00, BND-01) with mathematical solvers yet to be fully implemented.
- The first planned API transport is local JSON-RPC 2.0 over stdio; HTTP and GUI will be implemented later.
- Bender operates independently and MUST NOT connect to Studium databases, Qt dependencies, or the Studium ORM.
