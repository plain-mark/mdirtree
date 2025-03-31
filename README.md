# mdirtree

Generate directory structures from ASCII art or Markdown files.

+ [CONTRIBUTION.md](CONTRIBUTION.md)

## Overview

mdirtree is a command-line tool that converts ASCII directory trees into actual directory structures. It can parse trees from various sources, including plain text files, standard input, or code blocks within Markdown files.

This is useful for quickly setting up project scaffolding, creating test directories, or documenting and implementing directory structures defined in documentation.

## Features

- Generate directory structure from ASCII tree diagrams
- Support for Markdown and text files
- Interactive input mode
- Dry run mode
- Comment support (using # after file/directory names)
- Special handling for common files (README.md, __init__.py, etc.)
- REST API for remote directory generation

## Installation

### Via pip

```bash
pip install mdirtree
```

### Setting up a development environment

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment:

```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Install in development mode:

```bash
pip install -e .
```

## Usage

### Basic usage

```bash
# Generate from Markdown file
mdirtree structure.md -o ./output_dir

# Generate from text file
mdirtree structure.txt -o ./output_dir

# Generate from stdin
mdirtree - -o ./output_dir

# Dry run (show planned operations without creating files)
mdirtree --dry-run structure.md

# Enable verbose logging
mdirtree -v structure.md -o ./output_dir
```

### Command-line Options

```
usage: mdirtree [-h] [--output OUTPUT] [--dry-run] [--verbose] [input]

Generate directory structure from ASCII art or Markdown files

positional arguments:
  input                 Input file (*.md, *.txt) or - for stdin

options:
  -h, --help            show this help message and exit
  --output OUTPUT, -o OUTPUT
                        Output directory (default: current directory)
  --dry-run, -d         Show planned operations without creating files
  --verbose, -v         Enable verbose logging
```

### Input Format Example

```
project/
├── src/
│   ├── main.py
│   └── utils/
└── tests/
    └── test_main.py
```

## REST API

mdirtree also offers a REST API for generating directory structures:

### Starting the server

```python
from mdirtree.rest.server import run_server

run_server(host='0.0.0.0', port=5000)
```

### Using the client

```python
from mdirtree.rest.client import MdirtreeClient

client = MdirtreeClient('http://localhost:5000')

structure = """
project/
├── src/
│   └── main.py
└── tests/
    └── test_main.py
"""

# Generate structure
result = client.generate_structure(structure, output_path="./output")
print(result)

# Dry run mode
result = client.generate_structure(structure, dry_run=True)
print(result)
```

### REST API Endpoints

- POST /generate
  - Request body:
    ```json
    {
        "structure": "ASCII art structure",
        "output_path": "optional output path",
        "dry_run": false
    }
    ```
  - Response:
    ```json
    {
        "status": "success",
        "operations": ["list of operations"],
        "output_path": "output path"
    }
    ```

## License

[LICENSE](LICENSE)