#!/usr/bin/env python3
import os
import sys
import csv

def count_classes_in_package(package_dir):
    """
    Count the number of Java files (.java) present directly in the given directory.
    Files in subdirectories are not counted.
    """
    count = 0
    try:
        for item in os.listdir(package_dir):
            item_path = os.path.join(package_dir, item)
            # Only consider files that end with '.java'
            if os.path.isfile(item_path) and item.endswith('.java'):
                count += 1
    except Exception as e:
        print(f"Error accessing {package_dir}: {e}")
    return count

def find_packages(root_dir):
    """
    Walk through the directory tree starting at root_dir.
    Treat each directory containing at least one .java file as a package.
    Return a list of tuples (package_directory, num_classes).
    """
    packages = []
    for current_dir, subdirs, files in os.walk(root_dir):
        # Count .java files in the current directory only
        num_classes = 0
        for filename in files:
            if filename.endswith('.java'):
                num_classes += 1
        if num_classes > 0:
            packages.append((current_dir, num_classes))
    return packages

def write_average_to_csv(average, output_path):
    """
    Write the computed average to a CSV file.
    The CSV file will have a header and a single value for the average.
    Overwrites the file if it exists.
    """
    try:
        with open(output_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["average_classes"])
            writer.writerow([average])
        print(f"Average classes per package written to: {output_path}")
    except Exception as e:
        print(f"Error writing to {output_path}: {e}")

def main():
    # Verify command-line arguments
    if len(sys.argv) != 2:
        print("Usage: python calculate_average.py <directory>")
        sys.exit(1)

    root_dir = sys.argv[1]

    if not os.path.isdir(root_dir):
        print(f"Error: The directory '{root_dir}' does not exist or is not a valid directory.")
        sys.exit(1)

    # Find all packages and count classes in each
    packages = find_packages(root_dir)

    if not packages:
        print("No packages with Java files were found in the specified directory.")
        average = 0
    else:
        total_classes = sum(count for _, count in packages)
        num_packages = len(packages)
        average = total_classes / num_packages
        print(f"Found {num_packages} packages with a total of {total_classes} classes.")

    # Create the output CSV file in the same directory as this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_csv = os.path.join(script_dir, "average_classes.csv")
    write_average_to_csv(average, output_csv)

if __name__ == "__main__":
    main()
