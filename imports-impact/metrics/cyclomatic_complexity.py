#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2021-2025 Yegor Bugayenko
# SPDX-License-Identifier: MIT

import sys
from typing import Final
try:
    from javalang import tree, parse
except ImportError:
    # Create empty output file if javalang not available
    with open(sys.argv[2], 'w') as f:
        f.write("")
    sys.exit(0)
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
    print("WMC metric is: " + metrics)
    with open(java, encoding='utf-8', errors='ignore') as f:
        try:
            all = 0
            static = 0
            complexity: int = 0
            amount = 0
            ast = parse.parse(f.read())
            class_name = os.path.basename(java).replace('.java', '')
            for path, node in ast:
                if isinstance(node, tree.MethodDeclaration):
                    currentComplexity = method_complexity(node)
                    complexity += currentComplexity
                    amount += 1
                    method_name = node.name
                    is_static = "static" if "static" in node.modifiers else "instance"
                    all += 1
                    if "static" in node.modifiers: amount += 1

                    # Calculate number of parameters
                    parameter_count = len(node.parameters) if node.parameters else 0

                    # Define the CSV file path (in the same directory as the metrics file)
                    base_path = os.path.dirname(metrics)  # Get the directory of the metrics file
                    csv_path = os.path.join(base_path, f"{class_name}.csv")
                    # Write the method's details into the CSV file
                    file_exists = os.path.exists(csv_path)

                    with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
                        csv_writer = csv.writer(csvfile)
                        print(csv_path)

                        # Write the header only if the file is newly created
                        if not file_exists:
                            csv_writer.writerow(['methodName', 'isStatic', 'cyclomaticComplexity', 'parameterCount'])

                        # Write the current method's details
                        print("calc method complexity")
                        csv_writer.writerow([method_name, is_static, method_complexity(node), parameter_count])
            with open(metrics, 'a', encoding='utf-8') as m:
                m.write(f'WMC {complexity / all} Total \
                    Cyclomatic Complexity~\\citep{{mccabe1976complexity}} \
                    of all methods\n')
                m.write(f'CC {complexity} Total \
                                    Cyclomatic Complexity~\\citep{{mccabe1976complexity}} \
                                    of all methods\n')

        except FileNotFoundError as exception:
            message = f"{type(exception).__name__} {str(exception)}: {java}"
            sys.exit(message)