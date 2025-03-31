# src/mdirtree/generator.py

import os
import re
import logging
from typing import List, Tuple, Dict
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class DirectoryStructureGenerator:
    def __init__(self, ascii_structure: str):
        self.ascii_structure = ascii_structure
        self.base_indent = 0
        self.comment_pattern = re.compile(r'#.*$')
        self.structure: Dict[str, Dict] = {}
        self.logger = logging.getLogger(__name__)

        # Print input structure for debugging
        self.logger.info("Input ASCII structure:")
        for line in ascii_structure.split('\n'):
            self.logger.info(f"RAW LINE: '{line}'")

    def calculate_indent_level(self, line: str) -> int:
        """Calculate indent level for a line."""
        raw_indent = len(line) - len(line.lstrip())
        self.logger.debug(f"Raw indent: {raw_indent} for line: '{line}'")

        if self.base_indent == 0 and raw_indent > 0:
            self.base_indent = raw_indent
            self.logger.info(f"Set base indent to: {self.base_indent}")

        if self.base_indent > 0:
            level = raw_indent // self.base_indent
            self.logger.debug(f"Calculated level: {level} (raw_indent: {raw_indent} / base_indent: {self.base_indent})")
            return level
        return 0

    def parse_line(self, line: str) -> Tuple[int, str, str]:
        """Parse a single line of ASCII art."""
        self.logger.info(f"Parsing line: '{line}'")

        # Skip empty lines or lines with only vertical bars
        if not line.strip() or line.strip() == '│':
            self.logger.info(f"Skipping line: '{line}'")
            return -1, "", ""

        # Clean the line
        clean_line = line.replace('├──', '').replace('│', '').replace('└──', '')
        self.logger.debug(f"Cleaned line: '{clean_line}'")

        # Calculate indent level
        indent_level = self.calculate_indent_level(line)
        self.logger.info(f"Indent level: {indent_level}")

        # Extract comment
        comment_match = self.comment_pattern.search(clean_line)
        comment = comment_match.group().strip('# ') if comment_match else ''
        self.logger.debug(f"Extracted comment: '{comment}'")

        # Get name
        name = self.comment_pattern.sub('', clean_line).strip()
        self.logger.info(f"Extracted name: '{name}'")

        return indent_level, name, comment

    def build_tree_structure(self) -> None:
        """Build a tree structure from ASCII art."""
        self.logger.info("Starting tree structure building...")

        current_path: List[str] = []
        current_level = -1

        lines = [line for line in self.ascii_structure.strip().split('\n') if line.strip()]
        self.logger.info(f"Processing {len(lines)} non-empty lines")

        for i, line in enumerate(lines, 1):
            self.logger.info(f"\nProcessing line {i}/{len(lines)}: '{line}'")

            if line.strip().startswith('│'):
                self.logger.debug("Skipping vertical line")
                continue

            level, name, comment = self.parse_line(line)
            self.logger.info(f"Parsed components - Level: {level}, Name: '{name}', Comment: '{comment}'")

            # Path adjustment
            self.logger.debug(f"Current path before adjustment: {current_path}")
            self.logger.debug(f"Current level: {current_level}, New level: {level}")

            # Move up in the tree if needed
            while len(current_path) > level:
                removed = current_path.pop()
                self.logger.info(f"Moving up tree, removed: '{removed}'")

            # Clean last path component if going deeper
            if level > current_level and current_path:
                current_path[-1] = current_path[-1].rstrip('/')
                self.logger.debug(f"Cleaned last path component: {current_path[-1]}")

            # Update path
            current_path.append(name)
            current_level = level
            self.logger.info(f"Updated path: {' -> '.join(current_path)}")

            # Calculate full path
            path_components = [p.rstrip('/') for p in current_path[:-1]]
            if path_components:
                full_path = os.path.join(*path_components)
            else:
                full_path = '.'
            self.logger.info(f"Calculated full path: '{full_path}'")

            # Store in structure

            if full_path not in self.structure:
                self.structure[full_path] = {'files': [], 'dirs': [], 'comments': {}}
                self.logger.info(f"Created new structure entry for: '{full_path}'")

            if name.endswith('/'):
                clean_name = name.rstrip('/')
                self.structure[full_path]['dirs'].append(clean_name)
                self.logger.info(f"Added directory '{clean_name}' to '{full_path}'")
            else:
                self.structure[full_path]['files'].append(name)
                self.logger.info(f"Added file '{name}' to '{full_path}'")

            if comment:
                self.structure[full_path]['comments'][name] = comment
                self.logger.debug(f"Added comment for '{name}': {comment}")

        self.logger.info("\nFinal structure:")
        for path, content in self.structure.items():
            self.logger.info(f"\nPath: {path}")
            self.logger.info(f"Directories: {content['dirs']}")
            self.logger.info(f"Files: {content['files']}")
            self.logger.info(f"Comments: {content['comments']}")

    def generate_structure(self, base_path: str = '.', dry_run: bool = False) -> List[str]:
        """Generate directory structure from ASCII art."""
        self.logger.info(f"\nStarting structure generation in {base_path}")
        self.logger.info(f"Mode: {'Dry run' if dry_run else 'Actual generation'}")

        operations = []
        base_path = os.path.abspath(base_path)

        # Build structure first
        self.build_tree_structure()

        if not self.structure:
            self.logger.error("No structure was built! Check the input format.")
            return operations

        self.logger.info(f"Creating base directory at {base_path}")
        if not dry_run:
            os.makedirs(base_path, exist_ok=True)

        # Create the structure
        for path, content in self.structure.items():
            full_path = os.path.join(base_path, path) if path != '.' else base_path
            self.logger.info(f"\nProcessing path: {full_path}")

            # Create directories
            for dir_name in content['dirs']:
                dir_path = os.path.join(full_path, dir_name)
                operations.append(f"CREATE DIR: {dir_path}")
                self.logger.info(f"Creating directory: {dir_path}")
                if not dry_run:
                    os.makedirs(dir_path, exist_ok=True)

            # Create files
            for file_name in content['files']:
                file_path = os.path.join(full_path, file_name)
                operations.append(f"CREATE FILE: {file_path}")
                self.logger.info(f"Creating file: {file_path}")

                if not dry_run:
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        comment = content['comments'].get(file_name, '')
                        if comment:
                            f.write(f"# {comment}\n")

                        if file_name == '__init__.py':
                            pass
                        elif file_name == 'requirements.txt':
                            f.write("# Project dependencies\n")
                        elif file_name == '.gitignore':
                            f.write("__pycache__/\n*.pyc\n.env\n")
                        elif file_name == 'README.md':
                            f.write("# Project Documentation\n\n## Overview\n\n")
                        elif file_name.endswith('.py'):
                            f.write(f'"""\n{file_name}\n"""\n\n')

        self.logger.info(f"\nStructure generation completed.")
        self.logger.info(f"Total operations: {len(operations)}")
        return operations


def generate_from_ascii(ascii_structure: str, base_path: str = '.', dry_run: bool = False) -> List[str]:
    """Helper function to generate structure from ASCII art."""
    generator = DirectoryStructureGenerator(ascii_structure)
    return generator.generate_structure(base_path, dry_run)