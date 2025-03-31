import os
import re
import logging
from typing import List, Tuple, Dict, Optional
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class DirectoryStructureGenerator:
    def __init__(self, ascii_structure: str):
        self.ascii_structure = ascii_structure
        self.structure: Dict[str, Dict] = {}
        self.logger = logging.getLogger(__name__)

        # Print input structure for debugging
        self.logger.info("Input ASCII structure:")
        for line in ascii_structure.split('\n'):
            self.logger.info(f"RAW LINE: '{line}'")
        self.logger.info("")

    def _calculate_indent_level(self, line: str) -> int:
        """Calculate the indentation level of a line based on tree structure patterns."""
        # Count indentation units (each '│   ' pattern counts as one unit)
        indent_units = 0
        i = 0

        # For detailed debugging
        self.logger.debug(f"Analyzing indentation for line: '{line}'")

        # Count each unit of indentation ('│   ' pattern)
        while i < len(line):
            if i + 4 <= len(line) and line[i:i + 4] == '│   ':
                indent_units += 1
                i += 4
                self.logger.debug(f"Found '│   ' pattern at position {i - 4}, indent_units now {indent_units}")
            elif i + 4 <= len(line) and line[i:i + 4] == '    ':
                # Handle case for examples directory (spaces only)
                indent_units += 1
                i += 4
                self.logger.debug(f"Found '    ' pattern at position {i - 4}, indent_units now {indent_units}")
            elif line[i:i + 1] in ['├', '└', ' ']:
                # Skip branch markers or spaces at current position
                i += 1
            else:
                # Found non-indent character, we're done counting
                break

        self.logger.debug(f"Final indent level: {indent_units} for line '{line}'")
        return indent_units

    def parse_tree(self) -> None:
        """Parse the ASCII tree structure into a directory hierarchy."""
        self.logger.info("Building directory structure...")

        lines = [line for line in self.ascii_structure.strip().split('\n') if line.strip()]
        self.logger.info(f"Processing {len(lines)} non-empty lines")

        # Initialize the root path and structure
        root_dir = None

        # Process each line
        for i, line in enumerate(lines, 1):
            self.logger.info(f"\nProcessing line {i}/{len(lines)}: '{line}'")

            # Skip empty lines or lines with only vertical bars
            if not line.strip() or line.strip() == '│':
                self.logger.info("Skipping empty line or vertical bar")
                continue

            # Calculate indentation level
            indent_level = self._calculate_indent_level(line)
            self.logger.info(f"Indent level: {indent_level}")

            # Clean the line by removing all tree markers and leading/trailing whitespace
            clean_line = line.strip()
            # Replace tree branch markers
            if "├── " in clean_line:
                clean_line = clean_line.replace("├── ", "", 1)
            elif "└── " in clean_line:
                clean_line = clean_line.replace("└── ", "", 1)
            # Remove any remaining tree characters
            clean_line = clean_line.replace("│", "").strip()

            # Extract comment if present
            comment = ""
            if '#' in clean_line:
                parts = clean_line.split('#', 1)
                clean_line = parts[0].strip()
                comment = parts[1].strip()

            self.logger.info(f"Name: '{clean_line}', Comment: '{comment}'")

            # Skip lines with empty names
            if not clean_line:
                self.logger.info("Skipping line with empty name")
                continue

            # Determine if this is a directory or file
            is_dir = clean_line.endswith('/')
            name = clean_line.rstrip('/')

            # Set root directory if this is the first line
            if i == 1 and is_dir:
                root_dir = name
                self.logger.info(f"Set root directory: '{root_dir}'")
                self.structure[root_dir] = {'files': [], 'dirs': [], 'comments': {}}
                continue

            # Find parent directory based on indent level
            parent_dir = self._find_parent_dir(root_dir, indent_level, i, lines)
            self.logger.info(f"Parent directory: '{parent_dir}'")

            # Ensure parent exists in structure
            if parent_dir not in self.structure:
                self.logger.info(f"Creating new structure entry for: '{parent_dir}'")
                self.structure[parent_dir] = {'files': [], 'dirs': [], 'comments': {}}

            # Add file or directory to parent
            if is_dir:
                # Create directory path
                dir_path = os.path.join(parent_dir, name)

                # Add to parent's dirs list
                if name not in self.structure[parent_dir]['dirs']:
                    self.structure[parent_dir]['dirs'].append(name)
                    self.logger.info(f"Added directory '{name}' to '{parent_dir}'")

                # Initialize directory in structure
                if dir_path not in self.structure:
                    self.structure[dir_path] = {'files': [], 'dirs': [], 'comments': {}}
            else:
                # Add file to parent
                if name not in self.structure[parent_dir]['files']:
                    self.structure[parent_dir]['files'].append(name)
                    self.logger.info(f"Added file '{name}' to '{parent_dir}'")

            # Add comment if present
            if comment:
                self.structure[parent_dir]['comments'][name] = comment
                self.logger.info(f"Added comment for '{name}': '{comment}'")

        self.logger.info("\nFinal structure:")
        for path, content in self.structure.items():
            self.logger.info(f"\nPath: {path}")
            self.logger.info(f"Directories: {content['dirs']}")
            self.logger.info(f"Files: {content['files']}")
            self.logger.info(f"Comments: {content['comments']}")

    def _find_parent_dir(self, root_dir: str, indent_level: int, current_line_idx: int, lines: List[str]) -> str:
        """Find the parent directory for a line based on indent level and previous lines."""
        # Root level items belong to root_dir
        if indent_level == 0:
            return root_dir

        # For indented items, scan back to find the parent
        parent_path = []
        if root_dir:
            parent_path.append(root_dir)

        # Debug logging
        self.logger.debug(f"Finding parent for indent level {indent_level}, line index {current_line_idx}")

        # Scan backward to find parent directories at correct indent levels
        for j in range(current_line_idx - 1, 0, -1):
            prev_line = lines[j - 1]

            # Skip empty or vertical bar lines
            if not prev_line.strip() or prev_line.strip() == '│':
                continue

            # Calculate indent of previous line
            prev_indent = self._calculate_indent_level(prev_line)
            self.logger.debug(f"Checking line {j}: '{prev_line}', indent: {prev_indent}")

            # If we found a potential parent (line with indent level one less than current)
            if prev_indent == indent_level - 1:
                # Clean and extract the name
                prev_clean = prev_line.strip()
                if "├── " in prev_clean:
                    prev_clean = prev_clean.replace("├── ", "", 1)
                elif "└── " in prev_clean:
                    prev_clean = prev_clean.replace("└── ", "", 1)
                prev_clean = prev_clean.replace("│", "").strip()

                # Remove comment if any
                if '#' in prev_clean:
                    prev_clean = prev_clean.split('#', 1)[0].strip()

                # If it's a directory, it can be a parent
                if prev_clean.endswith('/'):
                    dir_name = prev_clean.rstrip('/')
                    self.logger.debug(f"Found potential parent dir: '{dir_name}' at level {prev_indent}")

                    # For items at indent 1, check if this is a direct child of root
                    if indent_level == 1:
                        return os.path.join(root_dir, dir_name)
                    else:
                        # For deeper nesting, check if the directory already exists in our structure
                        # and return its full path if found
                        for path in self.structure.keys():
                            if path.endswith('/' + dir_name):
                                self.logger.debug(f"Found existing parent path: '{path}'")
                                return path

        # Fallback to root if no parent found
        self.logger.debug(f"No parent found, using root directory: '{root_dir}'")
        return root_dir

    def generate_structure(self, base_path: str = '.', dry_run: bool = False) -> List[str]:
        """Generate the actual directory structure on disk."""
        self.logger.info(f"Starting structure generation in {base_path}")
        self.logger.info(f"Mode: {'Dry run' if dry_run else 'Actual generation'}")

        operations = []
        base_path = os.path.abspath(base_path)

        # Parse the tree structure
        self.parse_tree()

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

            # Create the directory itself if it doesn't already exist
            if path_str != '.' and not os.path.exists(full_path) and not dry_run:
                os.makedirs(full_path, exist_ok=True)
                operations.append(f"CREATE DIR: {full_path}")
                self.logger.info(f"Created directory: {full_path}")

            # Create directories
            for dir_name in content['dirs']:
                dir_path = os.path.join(full_path, dir_name)
                operations.append(f"CREATE DIR: {dir_path}")
                self.logger.info(f"Creating directory: {dir_path}")
                if not dry_run:
                    os.makedirs(dir_path, exist_ok=True)

            # Create files
            for file_name in content['files']:
                # Skip any empty filenames (final safety check)
                if not file_name.strip():
                    self.logger.info(f"Skipping empty filename during file creation")
                    continue

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