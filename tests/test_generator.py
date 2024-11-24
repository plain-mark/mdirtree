import pytest
import os
import tempfile
from mdirtree.generator import DirectoryStructureGenerator


@pytest.fixture
def simple_structure():
    return """
    project/
    ├── src/
    │   ├── main.py
    │   └── utils/
    └── tests/
        └── test_main.py
    """


def test_parse_line():
    generator = DirectoryStructureGenerator("")
    line = "├── src/ # Source directory"
    indent_level, name, comment = generator.parse_line(line)
    assert name == "src"
    assert comment == "Source directory"
    assert indent_level == 0


def test_generate_structure(simple_structure):
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = DirectoryStructureGenerator(simple_structure)
        operations = generator.generate_structure(tmpdir)

        assert os.path.exists(os.path.join(tmpdir, "project"))
        assert os.path.exists(os.path.join(tmpdir, "project", "src"))
        assert os.path.exists(os.path.join(tmpdir, "project", "src", "main.py"))
        assert os.path.exists(os.path.join(tmpdir, "project", "tests"))


def test_dry_run(simple_structure):
    generator = DirectoryStructureGenerator(simple_structure)
    operations = generator.generate_structure("dummy_path", dry_run=True)

    assert len(operations) > 0
    assert all(op.startswith(("CREATE DIR:", "CREATE FILE:")) for op in operations)
