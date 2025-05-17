#!/usr/bin/env python3
"""
LCOM4 Calculator for Java Classes using javalang
Usage: python3 lcom4_calculator.py <path_to_java_file>
"""

import sys
try:
    from javalang import tree, parse
except ImportError:
    # Create empty output file if javalang not available
    with open(sys.argv[2], 'w') as f:
        f.write("")
    sys.exit(0)
from collections import defaultdict
from typing import Final


def build_access_graph(java_code):
    """
    Builds a method-field interaction graph for LCOM4 calculation.
    Returns:
        graph (dict): Adjacency list of method/field connections
        methods (set): All method names in the class
        fields (set): All field names in the class
    """
    tree = javalang.parse.parse(java_code)
    graph = defaultdict(set)
    methods = set()
    fields = set()

    # Extract field declarations
    for _, node in tree.filter(javalang.tree.FieldDeclaration):
        for declarator in node.declarators:
            fields.add(declarator.name)

    # Extract method-field interactions
    for path, node in tree.filter(javalang.tree.MethodDeclaration):
        method_name = node.name
        methods.add(method_name)

        # Find all field accesses within the method
        for _, ref in node.filter(javalang.tree.MemberReference):
            if (not ref.qualifier) or (ref.qualifier == 'this'):
                if ref.member in fields:
                    graph[method_name].add(ref.member)
                    graph[ref.member].add(method_name)

        # Find method calls that access fields
        for _, call in node.filter(javalang.tree.MethodInvocation):
            if call.member in methods:
                graph[method_name].add(call.member)

    return graph, methods, fields

def calculate_lcom4(graph, methods):
    """
    Calculates LCOM4 by finding connected components in the graph.
    Returns:
        int: Number of connected components (higher = worse cohesion)
    """
    visited = set()
    components = 0

    def dfs(node):
        stack = [node]
        while stack:
            current = stack.pop()
            if current not in visited:
                visited.add(current)
                stack.extend(graph[current] - visited)

    for method in methods:
        if method not in visited:
            dfs(method)
            components += 1

    return components

def analyze_java_file(file_path):
    """Main analysis function for a Java file"""
    try:
        with open(file_path, 'r') as f:
            java_code = f.read()

        graph, methods, fields = build_access_graph(java_code)
        lcom4 = calculate_lcom4(graph, methods)

        return lcom4

        print(f"Java syntax error in {file_path}: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 lcom4_calculator.py <path_to_java_file>")
        sys.exit(1)
    java: Final[str] = sys.argv[1]
    metrics: Final[str] = sys.argv[2]
    with open(metrics, 'a', encoding='utf-8') as m:
        m.write(f'LCOM4 {analyze_java_file(sys.argv[1])} Total \
            Cyclomatic Complexity~\\citep{{mccabe1976complexity}} \
            of all methods\n')
