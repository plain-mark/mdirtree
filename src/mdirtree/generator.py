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

            # Calculate indentation level by counting spaces before tree markers
            spaces_before_content = 0
            for char in line:
                if char in [' ', '│']:
                    spaces_before_content += 1
                else:
                    break

            # Determine depth based on spaces (each level is 4 spaces)
            depth = spaces_before_content // 4
            self.logger.info(f"Depth: {depth}, Spaces: {spaces_before_content}")

            # Extract name by removing tree markers and leading/trailing whitespace
            clean_line = line.strip()
            if clean_line.startswith('├──'):
                clean_line = clean_line[3:].strip()
            elif clean_line.startswith('└──'):
                clean_line = clean_line[3:].strip()
            elif clean_line.startswith('│'):
                clean_line = clean_line[1:].strip()

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

            # Find parent directory based on depth
            if depth == 0:
                # Top-level items are direct children of root
                parent_dir = root_dir
            else:
                # Construct the path based on the depth and current position
                path_parts = []
                current_line = i - 1
                current_depth = depth

                # Work backwards to find all parent directories
                while current_line > 0 and current_depth > 0:
                    prev_line = lines[current_line - 1]
                    prev_spaces = 0
                    for char in prev_line:
                        if char in [' ', '│']:
                            prev_spaces += 1
                        else:
                            break

                    prev_depth = prev_spaces // 4

                    # If we found a parent (less depth), add it to path
                    if prev_depth < current_depth:
                        prev_name = prev_line.strip()
                        if prev_name.startswith('├──'):
                            prev_name = prev_name[3:].strip()
                        elif prev_name.startswith('└──'):
                            prev_name = prev_name[3:].strip()
                        elif prev_name.startswith('│'):
                            prev_name = prev_name[1:].strip()

                        if '#' in prev_name:
                            prev_name = prev_name.split('#', 1)[0].strip()

                        if prev_name.endswith('/'):
                            # It's a directory
                            path_parts.insert(0, prev_name.rstrip('/'))
                            current_depth = prev_depth

                    current_line -= 1

                # Construct the full path
                if root_dir:
                    path_parts.insert(0, root_dir)
                parent_dir = os.path.join(*path_parts)

            self.logger.info(f"Parent directory: '{parent_dir}'")

            # Ensure parent exists in structure
            if parent_dir not in self.structure:
                self.structure[parent_dir] = {'files': [], 'dirs': [], 'comments': {}}
                self.logger.info(f"Created new structure entry for: '{parent_dir}'")

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