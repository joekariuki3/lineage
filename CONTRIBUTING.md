# Contributing to Lineage

First off, thank you for considering contributing to Lineage! It's people like you that make Lineage a better tool for families to connect and preserve their histories.

The following is a set of guidelines for contributing to Lineage. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [How to Contribute](#how-to-contribute)
   - [Reporting Bugs](#reporting-bugs)
   - [Suggesting Enhancements](#suggesting-enhancements)
   - [Pull Requests](#pull-requests)
4. [Development Workflow](#development-workflow)
5. [Styleguides](#styleguides)

## Code of Conduct

This project and everyone participating in it is governed by a standard Code of Conduct. By participating, you are expected to uphold this code. Please be respectful, inclusive, and professional in all interactions.

## Getting Started

Ensure you have completed the local setup process defined in our [`README.md`](./README.md). You will need Python 3.11+, a virtual environment, and the dependencies listed in `requirements.txt` installed.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue in the GitHub repository. Include:

- A clear and descriptive title.
- Steps to reproduce the bug.
- Expected behavior vs. actual behavior.
- Screenshots or error logs if applicable.
- Your operating system and browser version.

### Suggesting Enhancements

We are always open to new features! When suggesting an enhancement, create an issue and include:

- A detailed description of the proposed feature.
- The problem it solves or the value it adds to the family tree experience.
- Potential implementation ideas (if you have them).

### Pull Requests

1. Fork the repo and create your branch from `develop` (or `master` if `develop` does not exist).
2. If you've added code that should be tested, add tests to the `tests/` directory.
3. Ensure the test suite passes by running `pytest`.
4. Update the documentation in the `docs/` directory or the `README.md` if you are changing application behavior or infrastructure.
5. Issue the pull request!

## Development Workflow

### Branching Strategy

- **`master`**: Contains stable, production-ready code.
- **`develop`**: The main integration branch for upcoming releases.
- **`feature/*`**: Used for developing new features (e.g., `feature/add-s3-photo-uploads`).
- **`bugfix/*`**: Used for fixing bugs (e.g., `bugfix/fix-spouse-rendering`).

### Running Tests

We enforce test coverage to maintain application stability. Before pushing your code, run:

```bash
pytest -v --cov=app --cov-report=term-missing

```

Ensure your new features do not drop the overall test coverage.

## Styleguides

### Python Conventions

- Follow [PEP 8](https://peps.python.org/pep-0008/) style guidelines.
- Use meaningful variable and function names.
- Document complex logic using docstrings (we prefer the Google or Sphinx docstring formats).
- Keep your routes, models, and services cleanly separated according to our Blueprint architecture.

### HTML/Tailwind Conventions

- Try to utilize Tailwind utility classes over writing custom CSS in `styles.css` whenever possible.
- Keep Jinja2 templates clean and use includes/macros for reusable components (like the SVG icons).

---

_Thank you for contributing to Lineage!_
