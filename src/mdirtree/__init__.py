"""
mdirtree - Generate directory structures from ASCII art or Markdown files.
"""

from .generator import DirectoryStructureGenerator
from .cli import main

__version__ = "0.1.0"
__all__ = ["DirectoryStructureGenerator", "main"]
