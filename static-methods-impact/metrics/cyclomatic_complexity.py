#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2021-2025 Yegor Bugayenko
# SPDX-License-Identifier: MIT

import sys
from typing import Final
from javalang import tree, parse
import os
import csv
sys.setrecursionlimit(10000)


def branches(parser_class: tree.CompilationUnit) -> int:
    """Determines the number of branches for a node
    according to the Extended Cyclomatic Complexity metric.
    Binary operations (&&, ||) and each case statement
    are taken into account.
    """
    count = 0
    if isinstance(parser_class, tree.BinaryOperation):
        if parser_class.operator in ('&&', '||'):
            count = 1
    elif isinstance(
        parser_class,
        (
            tree.ForStatement,
            tree.IfStatement,
            tree.WhileStatement,
            tree.DoStatement,
            tree.TernaryExpression,
            tree.MethodDeclaration
        )
    ):
        count = 1
    elif isinstance(parser_class, tree.SwitchStatementCase):
        count = 1
    elif isinstance(parser_class, tree.TryStatement):
        count = 1
    return count


def method_complexity(node) -> int:
    """
    Recursively calculates the cyclomatic complexity of a method by traversing its AST.
    """
    complexity = 0

    for path, n in node:
        complexity += branches(n)

    return complexity

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python cyclomatic_complexity.py <path to the .java file> <output file with metrics>")
        sys.exit(1)

    java: Final[str] = sys.argv[1]
    metrics: Final[str] = sys.argv[2]
    with open(java, encoding='utf-8', errors='ignore') as f:
        try:
            complexity: int = 1
            ast = parse.parse(f.read())
            class_name = os.path.basename(java).replace('.java', '')
            for path, node in ast:
                currentComplexity = branches(node)
                complexity += currentComplexity
                if isinstance(node, tree.MethodDeclaration):
                    method_name = node.name
                    is_static = "static" if "static" in node.modifiers else "instance"

                    # Define the CSV file path (in the same directory as the metrics file)
                    base_path = os.path.dirname(metrics)  # Get the directory of the metrics file
                    csv_path = os.path.join(base_path, f"{class_name}.csv")
                    # Write the method's details into the CSV file
                    file_exists = os.path.exists(csv_path)

                    with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
                        csv_writer = csv.writer(csvfile)

                        # Write the header only if the file is newly created
                        if not file_exists:
                            csv_writer.writerow(['methodName', 'isStatic', 'cyclomaticComplexity'])

                        # Write the current method's details
                        print("calc method complexity")
                        csv_writer.writerow([method_name, is_static, method_complexity(node)])
            with open(metrics, 'a', encoding='utf-8') as m:
                m.write(f'CC {complexity} Total \
                    Cyclomatic Complexity~\\citep{{mccabe1976complexity}} \
                    of all methods\n')

        except FileNotFoundError as exception:
            message = f"{type(exception).__name__} {str(exception)}: {java}"
            sys.exit(message)
