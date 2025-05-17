#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2021-2025 Yegor Bugayenko
# SPDX-License-Identifier: MIT

import sys
from typing import Final
try:
    from javalang import tree, parse
except ImportError:
    with open(sys.argv[2], 'w') as f:
        f.write("")
    sys.exit(0)
import os
import csv
sys.setrecursionlimit(10000)

def method_fanout(method: tree.MethodDeclaration) -> set:
    """
    Collects all unique qualified external method calls in a method.
    Returns a set of strings like 'System.out.println'
    """
    calls = set()
    for _, node in method:
        if isinstance(node, tree.MethodInvocation) and node.qualifier:
            calls.add(f"{node.qualifier}.{node.member}")
    return calls

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python fanout.py <path to the .java file> <output file with metrics>")
        sys.exit(1)

    java: Final[str] = sys.argv[1]
    metrics: Final[str] = sys.argv[2]

    with open(java, encoding='utf-8', errors='ignore') as f:
        try:
            ast = parse.parse(f.read())
            class_name = os.path.basename(java).replace('.java', '')

            base_path = os.path.dirname(metrics)
            csv_path = os.path.join(base_path, f"{class_name}_fanout.csv")
            file_exists = os.path.exists(csv_path)

            all_calls = set()

            with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                if not file_exists:
                    writer.writerow(['methodName', 'fanOut'])

                for _, node in ast:
                    if isinstance(node, tree.MethodDeclaration):
                        calls = method_fanout(node)
                        all_calls.update(calls)
                        writer.writerow([node.name, len(calls)])

            with open(metrics, 'a', encoding='utf-8') as m:
                m.write(f'FANOUT {len(all_calls)} Total unique external method calls in {class_name}\n')

        except FileNotFoundError as exception:
            message = f"{type(exception).__name__} {str(exception)}: {java}"
            sys.exit(message)
        except Exception as e:
            print(f"Error processing {java}: {str(e)}")
            sys.exit(1)
