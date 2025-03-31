import os
import re
import logging
from typing import List, Tuple, Dict, Optional, Set
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
        self.logger.info("")

    def _extract_name_and_comment(self, line: str) -> Tuple[str, str]:
        """Extract the name and comment from a cleaned line."""
        # Clean the line (remove tree characters but preserve indentation)
        clean_line = line.replace('├── ', '').replace('└── ', '').replace('│', ' ')

        # Extract comment
        comment_match = self.comment_pattern.search(clean_line)
        comment = comment_match.group().strip('# ') if comment_match else ''

        # Get name
        name = self.comment_pattern.sub('', clean_line).strip()

        return name, comment

    def _calculate_indent_level(self, line: str) -> int:
        """Calculate the indentation level of a line."""
        # Count the leading spaces and tree characters for indent calculation
        indent = 0
        for char in line:
            if char in [' ', '│', '├', '└']:
                indent += 1
            else:
                break

        # Set base indent on first indented line
        if self.base_indent == 0 and indent > 0:
            self.base_indent = indent
            self.logger.info(f"Set base indent to: {self.base_indent}")

        # Calculate level
        if self.base_indent > 0:
            level = indent // self.base_indent
            return level
        return 0

    def build_structure(self) -> None:
        """Parse ASCII tree and build the directory structure."""
        self.logger.info("Building directory structure...")

        lines = [line for line in self.ascii_structure.strip().split('\n') if line.strip()]
        self.logger.info(f"Processing {len(lines)} non-empty lines")

        # Track current path (directories only)
        dir_path = []
        current_level = -1

        for i, line in enumerate(lines, 1):
            self.logger.info(f"\nProcessing line {i}/{len(lines)}: '{line}'")

            # Skip empty lines or lines with only vertical bars
            if not line.strip() or line.strip() == '│':
                self.logger.info(f"Skipping empty line or vertical bar")
                continue

            # Calculate indent level
            level = self._calculate_indent_level(line)
            self.logger.info(f"Indent level: {level}")

            # Extract name and comment
            name, comment = self._extract_name_and_comment(line)
            self.logger.info(f"Name: '{name}', Comment: '{comment}'")

            # Adjust directory path based on level
            self.logger.debug(f"Current dir path: {dir_path}")
            self.logger.debug(f"Current level: {current_level}, New level: {level}")

            # If we're going up or staying at the same level, remove directories
            while len(dir_path) > level:
                removed = dir_path.pop()
                self.logger.info(f"Moving up tree, removed: '{removed}'")

            # Get the current parent directory path
            if dir_path:
                parent_dir = '/'.join(dir_path)
            else:
                parent_dir = '.'

            # Determine if this is a directory or file
            is_dir = name.endswith('/')

            # Process as directory or file
            if is_dir:
                # Add directory to current path
                clean_name = name.rstrip('/')
                dir_path.append(clean_name)
                current_level = level

                # Store in structure
                if parent_dir not in self.structure:
                    self.structure[parent_dir] = {'files': [], 'dirs': [], 'comments': {}}
                    self.logger.info(f"Created new structure entry for: '{parent_dir}'")

                self.structure[parent_dir]['dirs'].append(clean_name)
                self.logger.info(f"Added directory '{clean_name}' to '{parent_dir}'")

                if comment:
                    self.structure[parent_dir]['comments'][name] = comment
            else:
                # For files, don't modify the path, just add to current directory
                if parent_dir not in self.structure:
                    self.structure[parent_dir] = {'files': [], 'dirs': [], 'comments': {}}
                    self.logger.info(f"Created new structure entry for: '{parent_dir}'")

                self.structure[parent_dir]['files'].append(name)
                self.logger.info(f"Added file '{name}' to '{parent_dir}'")

                if comment:
                    self.structure[parent_dir]['comments'][name] = comment
                    self.logger.debug(f"Added comment for '{name}': {comment}")

        self.logger.info("\nFinal structure:")
        for path, content in self.structure.items():
            self.logger.info(f"\nPath: {path}")
            self.logger.info(f"Directories: {content['dirs']}")
            self.logger.info(f"Files: {content['files']}")
            self.logger.info(f"Comments: {content['comments']}")

    def generate_structure(self, base_path: str = '.', dry_run: bool = False) -> List[str]:
        """Generate the actual directory structure on disk."""
        self.logger.info(f"Starting structure generation in {base_path}")
        self.logger.info(f"Mode: {'Dry run' if dry_run else 'Actual generation'}")

        operations = []
        base_path = os.path.abspath(base_path)

        # Build structure first
        self.build_structure()

        if not self.structure:
            self.logger.error("No structure was built! Check the input format.")
            return operations

        # Create base directory
        self.logger.info(f"Creating base directory at {base_path}")
        if not dry_run:
            os.makedirs(base_path, exist_ok=True)

        # Process each directory in the structure
        for path_str, content in self.structure.items():
            # Create full path
            full_path = os.path.join(base_path, path_str) if path_str != '.' else base_path
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
                    # Ensure parent directory exists
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)

                    # Create the file with appropriate content
                    with open(file_path, 'w', encoding='utf-8') as f:
                        comment = content['comments'].get(file_name, '')
                        if comment:
                            f.write(f"# {comment}\n")

                        # Add default content based on file type
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

        self.logger.info("\nStructure generation completed.")
        self.logger.info(f"Total operations: {len(operations)}")
        return operations


def generate_from_ascii(ascii_structure: str, base_path: str = '.', dry_run: bool = False) -> List[str]:
    """Helper function to generate structure from ASCII art."""
    generator = DirectoryStructureGenerator(ascii_structure)
    return generator.generate_structure(base_path, dry_run)