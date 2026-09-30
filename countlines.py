"""count_lines.py.

Utility script to scan the repository, count lines of code across all Python
scripts (excluding virtual environments and caches), and display a formatted summary.
"""

from dataclasses import dataclass
from pathlib import Path

# Directories to exclude from analysis
IGNORED_DIRS: set[str] = {
    ".venv",
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}


@dataclass(frozen=True)
class FileStats:
    """Statistics for an individual source file."""

    relative_path: str
    total_lines: int
    code_lines: int
    comment_lines: int
    blank_lines: int


def analyze_file(file_path: Path, root_path: Path) -> FileStats:
    """Parses a Python file to categorize its lines."""
    total = 0
    code = 0
    comments = 0
    blanks = 0

    with open(file_path, "r", encoding="utf-8") as f:
        in_multiline_docstring = False

        for line in f:
            total += 1
            stripped = line.strip()

            if not stripped:
                blanks += 1
                continue

            # Basic docstring and comment detection
            if stripped.startswith('"""') or stripped.startswith("'''"):
                comments += 1
                # If the docstring starts and ends on the same line (e.g. single-line docstring)
                if (
                    len(stripped) > 3
                    and (
                        stripped.endswith('"""')
                        or stripped.endswith("'''")
                    )
                ):
                    continue
                in_multiline_docstring = not in_multiline_docstring
                continue

            if in_multiline_docstring:
                comments += 1
                if stripped.endswith('"""') or stripped.endswith("'''"):
                    in_multiline_docstring = False
                continue

            if stripped.startswith("#"):
                comments += 1
            else:
                code += 1

    return FileStats(
        relative_path=str(file_path.relative_to(root_path)),
        total_lines=total,
        code_lines=code,
        comment_lines=comments,
        blank_lines=blanks,
    )


def main() -> None:
    root = Path(__file__).resolve().parent
    stats_list: list[FileStats] = []

    # Recursively collect all Python files not in ignored directories
    for path in root.rglob("*.py"):
        # Check if any parent folder matches our ignore set
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        stats_list.append(analyze_file(path, root))

    # Sort files alphabetically by path
    stats_list.sort(key=lambda s: s.relative_path)

    # Calculate column widths
    max_path_len = max(len(s.relative_path) for s in stats_list) if stats_list else 30
    path_col_width = max(max_path_len, 25)

    header = (
        f"{'File':<{path_col_width}} | "
        f"{'Total':>7} | "
        f"{'Code':>7} | "
        f"{'Comments':>8} | "
        f"{'Blank':>7}"
    )
    divider = "-" * len(header)

    print(divider)
    print(header)
    print(divider)

    total_lines = 0
    total_code = 0
    total_comments = 0
    total_blank = 0

    for s in stats_list:
        total_lines += s.total_lines
        total_code += s.code_lines
        total_comments += s.comment_lines
        total_blank += s.blank_lines

        print(
            f"{s.relative_path:<{path_col_width}} | "
            f"{s.total_lines:>7} | "
            f"{s.code_lines:>7} | "
            f"{s.comment_lines:>8} | "
            f"{s.blank_lines:>7}"
        )

    print(divider)
    summary = (
        f"{'TOTAL (' + str(len(stats_list)) + ' files)':<{path_col_width}} | "
        f"{total_lines:>7} | "
        f"{total_code:>7} | "
        f"{total_comments:>8} | "
        f"{total_blank:>7}"
    )
    print(summary)
    print(divider)


if __name__ == "__main__":
    main()