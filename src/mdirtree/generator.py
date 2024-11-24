import os
import re
from typing import List, Tuple, Optional


class DirectoryStructureGenerator:
    def __init__(self, ascii_structure: str):
        self.ascii_structure = ascii_structure
        self.base_indent = 0
        self.comment_pattern = re.compile(r"#.*$")

    def parse_line(self, line: str) -> Tuple[int, str, str]:
        """Parse a single line of ASCII art.

        Returns:
            Tuple of (indent_level, file_name, comment)
        """
        clean_line = line.replace("├──", "").replace("│", "").replace("└──", "")

        indent = len(line) - len(line.lstrip())
        if self.base_indent == 0 and indent > 0:
            self.base_indent = indent

        indent_level = (indent - self.base_indent) // 4 if self.base_indent > 0 else 0

        comment_match = self.comment_pattern.search(clean_line)
        comment = comment_match.group().strip("# ") if comment_match else ""

        name = self.comment_pattern.sub("", clean_line).strip()
        if name.endswith("/"):
            name = name[:-1]

        return indent_level, name, comment

    def generate_structure(
        self, base_path: str = ".", dry_run: bool = False
    ) -> List[str]:
        """Generate directory structure from ASCII art.

        Args:
            base_path: Base path for structure generation
            dry_run: If True, only show planned operations

        Returns:
            List of performed or planned operations
        """
        operations = []
        current_path = [base_path]

        for line in self.ascii_structure.strip().split("\n"):
            if not line.strip():
                continue

            indent_level, name, comment = self.parse_line(line)

            while len(current_path) > indent_level + 1:
                current_path.pop()

            full_path = os.path.join(*current_path, name)

            if name.endswith("/") or "." not in name:
                operations.append(f"CREATE DIR: {full_path}")
                if not dry_run:
                    os.makedirs(full_path, exist_ok=True)
                current_path.append(name)
            else:
                operations.append(f"CREATE FILE: {full_path}")
                if not dry_run:
                    with open(full_path, "w", encoding="utf-8") as f:
                        if comment:
                            f.write(f"# {comment}\n")

                    if name == "__init__.py":
                        pass
                    elif name == "requirements.txt":
                        with open(full_path, "w") as f:
                            f.write("# Project dependencies\n")
                    elif name == ".gitignore":
                        with open(full_path, "w") as f:
                            f.write("__pycache__/\n*.pyc\n.env\n")
                    elif name == "README.md":
                        with open(full_path, "w") as f:
                            f.write("# Project Documentation\n\n## Overview\n\n")

        return operations
