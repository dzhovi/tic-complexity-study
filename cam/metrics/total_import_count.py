#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2021-2025 Yegor Bugayenko
# SPDX-License-Identifier: MIT

import sys
from typing import Final
import os

def count_imports_from_file(java_file: str) -> (int, int):
    """
    Scans the beginning of a Java file to count import statements.
    It stops reading once it encounters a non-import line after starting to see imports.

    Early stop condition:
      - Once at least one import statement has been encountered (i.e. the import block
        has started), if a line is not empty, not a comment, and does not begin with 'import '
        (or is a package declaration), then we assume the block of import statements has ended.

    Returns:
        A tuple (regular_import_count, wildcard_import_count)
    """
    regular = 0
    wildcard = 0
    in_import_block = False

    try:
        with open(java_file, encoding='utf-8', errors='ignore') as f:
            for line in f:
                stripped = line.strip()
                # Skip empty lines or comments.
                if not stripped or stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
                    continue
                # Ignore package declarations.
                if stripped.startswith("package"):
                    continue

                # Process import statements.
                if stripped.startswith("import "):
                    in_import_block = True
                    # Check if the line is a wildcard import.
                    if stripped.endswith(".*;"):
                        wildcard += 1
                    else:
                        regular += 1
                    continue

                # Once we have seen an import statement and this line is not an import,
                # assume the import block is finished. This early-stop condition saves time.
                if in_import_block:
                    break

                # If no import statements have been encountered yet, continue scanning.
        return regular, wildcard

    except FileNotFoundError:
        print(f"File not found: {java_file}")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing file {java_file}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python import_counter.py <path to the .java file> <output file with metrics>")
        sys.exit(1)

    java: Final[str] = sys.argv[1]
    metrics: Final[str] = sys.argv[2]

    reg_count, wild_count = count_imports_from_file(java)
    class_name = os.path.basename(java).replace('.java', '')

    try:
        # Append metrics to the output file, creating it if needed.
        with open(metrics, 'a', encoding='utf-8') as m:
            m.write(f"IMP_REGULAR {reg_count} Number of regular import statements in {class_name}\n")
            m.write(f"IMP_WILDCARD {wild_count} Number of wildcard import statements in {class_name}\n")
    except Exception as e:
        print(f"Error writing metrics to {metrics}: {e}")
        sys.exit(1)
