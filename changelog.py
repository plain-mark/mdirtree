#!/bin/python
import subprocess
import os
import re
from datetime import datetime
from typing import List, Optional, Tuple, Dict


class ChangelogGenerator:
    def __init__(self):
        self.version: str = "0.1.0"
        self.changes: Dict[str, List[str]] = {
            "Added": [],
            "Changed": [],
            "Deprecated": [],
            "Removed": [],
            "Fixed": [],
            "Security": []
        }

    def get_git_diff(self, file_path: str, staged: bool = False) -> str:
        """Get git diff for a file."""
        try:
            if not os.path.exists(file_path) and not staged:
                return ""

            cmd = ['git', 'diff']
            if staged:
                cmd.append('--cached')
            cmd.append('--')
            cmd.append(file_path)

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )
            return result.stdout
        except subprocess.CalledProcessError:
            return ""

    def analyze_file_changes(self, file_path: str, staged: bool = False) -> str:
        """Analyze file changes to determine the type of change."""
        diff = self.get_git_diff(file_path, staged)

        # Simple rule-based classification
        if not os.path.exists(file_path) and not staged:
            return "Removed"
        elif os.path.exists(file_path) and not staged:
            return "Added" if "+++" in diff else "Changed"

        # For staged files
        if "new file" in diff:
            return "Added"
        elif "deleted file" in diff:
            return "Removed"
        elif "security" in diff.lower() or "vuln" in diff.lower():
            return "Security"
        elif "deprecat" in diff.lower():
            return "Deprecated"
        elif "fix" in diff.lower() or "bug" in diff.lower():
            return "Fixed"
        else:
            return "Changed"

    def add_change(self, change_type: str, message: str):
        """Add a change to the changelog."""
        if change_type in self.changes:
            self.changes[change_type].append(message)

    def generate_changelog(self, staged: bool = False) -> str:
        """Generate a changelog based on git changes."""
        try:
            # Get changed files
            if staged:
                result = subprocess.run(
                    ['git', 'diff', '--cached', '--name-only'],
                    capture_output=True,
                    text=True,
                    check=True
                )
            else:
                result = subprocess.run(
                    ['git', 'ls-files', '--modified', '--others', '--exclude-standard'],
                    capture_output=True,
                    text=True,
                    check=True
                )

            files = result.stdout.strip().split('\n')

            # Analyze each file
            for file in files:
                if file:
                    change_type = self.analyze_file_changes(file, staged)
                    self.add_change(change_type, f"Changes in {file}")

            # Generate markdown
            today = datetime.now().strftime("%Y-%m-%d")
            changelog = f"## [{self.version}] - {today}\n\n"

            for section, changes in self.changes.items():
                if changes:
                    changelog += f"### {section}\n"
                    for change in changes:
                        changelog += f"- {change}\n"
                    changelog += "\n"

            return changelog

        except subprocess.CalledProcessError as e:
            print(f"Error executing git command: {e}")
            return ""

    def update_changelog_file(self, output_file: str = "CHANGELOG.md", staged: bool = False):
        """Update the CHANGELOG.md file."""
        new_changes = self.generate_changelog(staged)
        if not new_changes:
            return

        try:
            existing_content = ""
            if os.path.exists(output_file):
                with open(output_file, 'r', encoding='utf-8') as f:
                    existing_content = f.read()

            with open(output_file, 'w', encoding='utf-8') as f:
                if not existing_content:
                    f.write("# Changelog\n\n")
                    f.write("All notable changes to this project will be documented in this file.\n\n")
                    f.write(new_changes)
                else:
                    # Insert new changes after the header
                    parts = existing_content.split('\n\n', 2)
                    f.write(parts[0] + '\n\n')
                    if len(parts) > 1:
                        f.write(parts[1] + '\n\n')
                    f.write(new_changes)
                    if len(parts) > 2:
                        f.write(parts[2])

        except Exception as e:
            print(f"Error updating changelog file: {e}")


def main():
    generator = ChangelogGenerator()
    generator.update_changelog_file(staged=True)


if __name__ == "__main__":
    main()