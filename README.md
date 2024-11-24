# mdirtree

Generate directory structures from ASCII art or Markdown files.

+ [CONTRIBUTION.md](CONTRIBUTION.md)

## Installation


### Setting up a virtual environment

Create a virtual environment

```bash
python -m venv venv
```

```bash
source venv/bin/activate
```

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

```bash
pip install -e .
```


## Usage

```bash
# Generate from Markdown file
mdirtree structure.md -o ./output_dir

# Generate from text file
mdirtree structure.txt -o ./output_dir

# Generate from stdin
mdirtree - -o ./output_dir

# Dry run (show planned operations without creating files)
mdirtree --dry-run structure.md
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

mdirtree oferuje również REST API do generowania struktur katalogów:

### Uruchomienie serwera

```python
from mdirtree.rest.server import run_server

run_server(host='0.0.0.0', port=5000)
```

### Użycie klienta

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

# Generowanie struktury
result = client.generate_structure(structure, output_path="./output")
print(result)

# Tryb dry run
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
    
## Features

- Generate directory structure from ASCII tree diagrams
- Support for Markdown and text files
- Interactive input mode
- Dry run mode
- Comment support (using # after file/directory names)
- Special handling for common files (README.md, __init__.py, etc.)

## License

[LICENSE](LICENSE)