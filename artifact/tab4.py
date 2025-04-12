#!/bin/python3
# This script generates a table comparing library coverage across different fuzzing campaigns.

import os
import csv
from prettytable import PrettyTable

base_dir = "../fuzzing_campaigns"  # Change if needed
# folders = [d for d in os.listdir(base_dir) if d.startswith("gen") and os.path.isdir(os.path.join(base_dir, d))]
folders = ["gen24_deep0", "gen18_deep6", "gen12_deep12", "gen6_deep18"] 

data = {}
libraries = set()

# Read each CSV
for folder in sorted(folders):
    csv_path = os.path.join(base_dir, folder, "total_library_coverage_per_iter.csv")
    if not os.path.exists(csv_path):
        continue

    data[folder] = {}
    with open(csv_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            lib, _, coverage = row
            data[folder][lib] = coverage
            libraries.add(lib)

# Build table
headers = ["Library"] + sorted(data.keys())
table = PrettyTable(headers)

for lib in sorted(libraries):
    row = [lib]
    for folder in sorted(data.keys()):
        row.append(data[folder].get(lib, "-"))
    table.add_row(row)

# Print table
print(table)
