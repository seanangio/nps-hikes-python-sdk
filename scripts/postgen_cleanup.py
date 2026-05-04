#!/usr/bin/env python3
"""Post-generation cleanup for datamodel-codegen output.

Removes unwanted classes and fixes RootModel wrappers so that the generated
models.py only contains SDK-relevant Pydantic BaseModel classes with plain
field types (no RootModel indirection).

Usage:
    python scripts/postgen_cleanup.py src/nps_hikes/models.py
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

# Classes that should be deleted entirely (not part of the SDK surface).
UNWANTED_CLASSES = frozenset(
    {
        "NlqRequest",
        "NlqResponse",
        "ValidationError",
        "HTTPValidationError",
    }
)


def _find_class_ranges(source: str) -> dict[str, tuple[int, int, ast.ClassDef]]:
    """Return {class_name: (start_line, end_line, node)} for every class."""
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    total_lines = len(lines)
    classes: dict[str, tuple[int, int, ast.ClassDef]] = {}

    top_level_nodes = [
        n for n in ast.iter_child_nodes(tree) if isinstance(n, ast.ClassDef)
    ]
    for i, node in enumerate(top_level_nodes):
        start = node.lineno  # 1-indexed
        if i + 1 < len(top_level_nodes):
            # End just before the next top-level class (excluding blank lines).
            end = top_level_nodes[i + 1].lineno - 1
            # Trim trailing blank lines between classes.
            while end > start and lines[end - 1].strip() == "":
                end -= 1
        else:
            end = total_lines
            while end > start and lines[end - 1].strip() == "":
                end -= 1
        classes[node.name] = (start, end, node)

    return classes


def _is_rootmodel_class(node: ast.ClassDef) -> bool:
    """Check if a class inherits from RootModel[...]."""
    for base in node.bases:
        if isinstance(base, ast.Subscript):
            if isinstance(base.value, ast.Name) and base.value.id == "RootModel":
                return True
    return False


def _extract_rootmodel_constraints(
    node: ast.ClassDef, source_lines: list[str]
) -> dict[str, str]:
    """Extract ge/le constraints from a RootModel class's Field() call."""
    constraints: dict[str, str] = {}
    # Read the raw text of the class body and look for ge=, le= in Field().
    start = node.lineno - 1
    end = node.end_lineno or start + 1
    body_text = "".join(source_lines[start:end])
    for match in re.finditer(r"\b(ge|le)\s*=\s*(-?[\d.]+)", body_text):
        constraints[match.group(1)] = match.group(2)
    return constraints


def run_cleanup(filepath: Path) -> bool:
    """Clean up the generated models file. Returns True if changes were made."""
    source = filepath.read_text()
    lines = source.splitlines(keepends=True)
    classes = _find_class_ranges(source)

    # Identify RootModel classes and collect their constraints.
    rootmodel_classes: dict[str, dict[str, str]] = {}
    for name, (_, _, node) in classes.items():
        if _is_rootmodel_class(node):
            rootmodel_classes[name] = _extract_rootmodel_constraints(node, lines)

    classes_to_remove = set()
    for name in classes:
        if name in UNWANTED_CLASSES or name in rootmodel_classes:
            classes_to_remove.add(name)

    if not classes_to_remove:
        return False

    # Collect line ranges to delete (convert to 0-indexed).
    ranges_to_delete: list[tuple[int, int]] = []
    for name in classes_to_remove:
        start, end, _ = classes[name]
        ranges_to_delete.append((start - 1, end))  # 0-indexed start, exclusive end

    # Sort descending so we can delete from bottom to top.
    ranges_to_delete.sort(key=lambda r: r[0], reverse=True)
    for start, end in ranges_to_delete:
        del lines[start:end]

    result = "".join(lines)

    # Replace RootModel type references and inline their constraints into the
    # adjacent Field() call.  We use a multiline regex that captures the type
    # name together with its Field() so only the correct Field() is modified.
    for rm_name, constraints in rootmodel_classes.items():
        constraint_str = ", ".join(f"{k}={v}" for k, v in constraints.items())

        def _replace_type_and_field(m: re.Match) -> str:
            type_part = m.group(1)  # e.g. "Latitude1 | None" or "Latitude1"
            between = m.group(2)  # whitespace/comma between type and Field
            field_call = m.group(3)  # the Field(...) content

            # Replace type name with float.
            new_type = re.sub(
                rf"\b{re.escape(rm_name)}\b", "float", type_part
            )
            # Add constraints to Field() if not already present.
            new_field = field_call
            if constraints and not all(
                f"{k}=" in field_call for k in constraints
            ):
                if "title=" in field_call:
                    new_field = field_call.replace(
                        "title=", f"{constraint_str}, title=", 1
                    )
                else:
                    new_field = re.sub(r"\)$", f", {constraint_str})", field_call)
            return new_type + between + new_field

        # Match: RootModel type ref, then whitespace/comma, then Field(...).
        # The Field() may span multiple lines, so use DOTALL.
        result = re.sub(
            rf"(\b{re.escape(rm_name)}\b[^,\n]*)"  # (1) type with optional "| None"
            rf"(,\s*\n\s*)"  # (2) comma + newline + indent
            rf"(Field\(.*?\))",  # (3) Field(...) call (non-greedy, multiline)
            _replace_type_and_field,
            result,
            flags=re.DOTALL,
        )

    # Clean up: remove RootModel from imports if no longer used.
    if "RootModel" not in result.split("from pydantic import", 1)[-1].split("\n")[0]:
        pass  # Already clean.
    result = re.sub(
        r"from pydantic import ([^;\n]*),\s*RootModel",
        r"from pydantic import \1",
        result,
    )
    result = re.sub(
        r"from pydantic import RootModel,\s*",
        "from pydantic import ",
        result,
    )

    # Collapse runs of 3+ blank lines down to 2.
    result = re.sub(r"\n{3,}", "\n\n\n", result)

    if result == source:
        return False

    filepath.write_text(result)
    return True


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <models.py>", file=sys.stderr)
        sys.exit(1)

    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print(f"Error: {filepath} not found", file=sys.stderr)
        sys.exit(1)

    changed = run_cleanup(filepath)
    if changed:
        print(f"Cleaned up {filepath}")
    else:
        print(f"No changes needed for {filepath}")


if __name__ == "__main__":
    main()
