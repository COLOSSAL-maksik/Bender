import ast
import os
from pathlib import Path

import pytest


def get_all_python_files(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                yield os.path.join(root, file)


def extract_imports(filepath, source_dir=None):
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    tree = ast.parse(content, filename=filepath)

    filepath_path = Path(filepath).resolve()
    if source_dir:
        source_dir_path = Path(source_dir).resolve()
        try:
            rel_path = filepath_path.relative_to(source_dir_path)
            package_parts = list(rel_path.parent.parts)
        except ValueError:
            package_parts = []
    else:
        parts = filepath_path.parts
        if "src" in parts:
            idx = parts.index("src")
            package_parts = list(parts[idx + 1 : -1])
        else:
            package_parts = []

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level > 0:
                if not package_parts:
                    continue

                base_parts = package_parts[: len(package_parts) - node.level + 1]
                full_module_parts = list(base_parts)
                if node.module:
                    full_module_parts.extend(node.module.split("."))
                    imports.add(".".join(full_module_parts))
                    # Also add specific aliases for relative imports
                    for alias in node.names:
                        imports.add(".".join(full_module_parts + [alias.name]))
                else:
                    for alias in node.names:
                        imports.add(".".join(full_module_parts + [alias.name]))
            elif node.module:
                imports.add(node.module)
                # Ensure we also capture specific aliases (e.g. from bender import reference)
                for alias in node.names:
                    imports.add(node.module + "." + alias.name)
    return imports


def check_no_imports(source_dir, forbidden_prefixes):
    violations = []
    for filepath in get_all_python_files(source_dir):
        # Allow checking test file itself for a simulated failure
        # In reality, this loop only processes source code in standard cases
        imports = extract_imports(filepath)
        for imp in imports:
            for prefix in forbidden_prefixes:
                if imp == prefix or imp.startswith(f"{prefix}."):
                    violations.append((filepath, imp))
    return violations


SRC_DIR = Path(__file__).resolve().parent.parent.parent.parent / "src"


def test_bender_does_not_import_studium():
    bender_dir = SRC_DIR / "bender"
    violations = check_no_imports(bender_dir, ["studium"])
    assert not violations, f"Forbidden imports found in bender -> studium: {violations}"


def test_bender_core_does_not_import_forbidden():
    core_dir = SRC_DIR / "bender" / "core"
    violations = check_no_imports(
        core_dir, ["bender.domains", "bender.methods", "bender.reference", "bender.adapters"],
    )
    assert not violations, f"Forbidden imports found in bender.core: {violations}"


def test_bender_methods_does_not_import_reference():
    methods_dir = SRC_DIR / "bender" / "methods"
    violations = check_no_imports(methods_dir, ["bender.reference"])
    assert not violations, f"Forbidden imports found in bender.methods: {violations}"


def test_bender_reference_does_not_import_methods():
    ref_dir = SRC_DIR / "bender" / "reference"
    violations = check_no_imports(ref_dir, ["bender.methods"])
    assert not violations, f"Forbidden imports found in bender.reference: {violations}"


def test_bender_graphics_does_not_import_solvers():
    graphics_dir = SRC_DIR / "bender" / "graphics"
    violations = check_no_imports(graphics_dir, ["bender.methods", "bender.reference"])
    assert not violations, f"Forbidden imports found in bender.graphics: {violations}"


def test_architecture_test_catches_violation(tmp_path):
    # Dummy file to test the check itself
    dummy_file = tmp_path / "dummy.py"
    dummy_file.write_text("import studium\n")
    imports = extract_imports(str(dummy_file))

    assert "studium" in imports

    # Test checking function
    violations = check_no_imports(tmp_path, ["studium"])
    assert len(violations) == 1
    assert violations[0][1] == "studium"


def test_architecture_test_handles_relative_imports(tmp_path):
    # Dummy package structure
    pkg_dir = tmp_path / "src" / "bender" / "methods"
    pkg_dir.mkdir(parents=True)
    dummy_file = pkg_dir / "foo.py"
    dummy_file.write_text(
        "from ..reference import y\nfrom .bar import x\nfrom ...studium import z\nimport os\nfrom ... import reference\n",
    )

    imports = extract_imports(str(dummy_file))

    assert "bender.reference" in imports
    assert "bender.reference.y" in imports
    assert "bender.methods.bar" in imports
    assert "bender.methods.bar.x" in imports
    assert "studium" in imports
    assert "studium.z" in imports
    assert "os" in imports


def test_architecture_test_catches_absolute_aliases(tmp_path):
    # Tests that `from bender import reference` is correctly tracked as `bender.reference`
    dummy_file = tmp_path / "dummy.py"
    dummy_file.write_text(
        "from bender import reference\nfrom bender import reference as ref\nfrom bender.methods import foo\n",
    )

    imports = extract_imports(str(dummy_file))
    assert "bender.reference" in imports
    assert "bender.methods" in imports
    assert "bender.methods.foo" in imports

    # We should catch violations if we check
    violations = check_no_imports(tmp_path, ["bender.reference"])
    assert len(violations) >= 1

    violations2 = check_no_imports(tmp_path, ["bender.methods"])
    assert len(violations2) >= 1


def test_architecture_test_fails_on_unreadable_file(tmp_path, monkeypatch):
    import builtins

    dummy_file = tmp_path / "src" / "bender" / "unreadable.py"
    dummy_file.parent.mkdir(parents=True, exist_ok=True)
    dummy_file.touch()

    original_open = builtins.open

    def mock_open(file, *args, **kwargs):
        if str(file) == str(dummy_file):
            raise PermissionError(f"Permission denied: {file}")
        return original_open(file, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", mock_open)

    with pytest.raises(PermissionError):
        extract_imports(str(dummy_file))


def test_architecture_test_fails_on_syntax_error(tmp_path):
    dummy_file = tmp_path / "src" / "bender" / "bad.py"
    dummy_file.parent.mkdir(parents=True, exist_ok=True)
    dummy_file.write_text("this is not valid python code = \n")

    with pytest.raises(SyntaxError):
        extract_imports(str(dummy_file))


def test_bender_core_catches_absolute_aliases_violations(tmp_path):
    # This verifies that domains, methods, and adapters in core raise an error
    core_dir = tmp_path / "src" / "bender" / "core"
    core_dir.mkdir(parents=True)
    dummy_file = core_dir / "bad_core.py"
    dummy_file.write_text(
        "from bender import domains\nfrom bender import methods as meth\nfrom bender.adapters import something\n",
    )

    # We should catch violations if we check
    violations = check_no_imports(tmp_path, ["bender.domains", "bender.methods", "bender.adapters"])
    # We expect at least one violation for each domain, methods, adapters
    assert any("bender.domains" in imp for f, imp in violations)
    assert any("bender.methods" in imp for f, imp in violations)
    assert any("bender.adapters" in imp for f, imp in violations)


def test_bender_cross_dependencies_catches_aliases_violations(tmp_path):
    # reference -> methods
    ref_dir = tmp_path / "src" / "bender" / "reference"
    ref_dir.mkdir(parents=True)
    dummy_ref = ref_dir / "bad_ref.py"
    dummy_ref.write_text("from bender import methods\n")

    # methods -> reference
    meth_dir = tmp_path / "src" / "bender" / "methods"
    meth_dir.mkdir(parents=True)
    dummy_meth = meth_dir / "bad_meth.py"
    dummy_meth.write_text("from bender import reference\n")

    violations_ref = check_no_imports(ref_dir, ["bender.methods"])
    assert len(violations_ref) >= 1
    assert any("bender.methods" in imp for f, imp in violations_ref)

    violations_meth = check_no_imports(meth_dir, ["bender.reference"])
    assert len(violations_meth) >= 1
    assert any("bender.reference" in imp for f, imp in violations_meth)
