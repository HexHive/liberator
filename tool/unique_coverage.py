#!/usr/bin/env python3

from collections import Counter, defaultdict
import argparse
import os


class File:
    """
    Represents a file with its filename and lines.
    """
    def total_visits(self):
        return sum(self.lines.values())

    def __init__(self):
        self.filename = ""
        self.lines = Counter()
    
    def unique_visits(self, fileB):
        d = defaultdict(lambda: 1, {})
        [d[v] for v in set(self.lines.keys()) - set(fileB.lines.keys())]
        diff = File()
        diff.lines = d
        diff.filename = self.filename
        return diff

    def merge(self, fileB):
        for k, v in fileB.lines.items():
            self.lines[k] += v

class Library:
    """
    Represents a library with files and their coverage information.
    """
    def __init__(self, log_file_path):
        self.files = {}
        self.log_file_path = log_file_path
        self.parse_log_file()

    def get_all_files(self):
        return list(self.files.keys())

    def parse_log_file(self):
        """
        Parses the log file and populates the library with file coverage information.
        The log file should contain lines in the following format:
        - /home/<username>/path/to/file.py
        - line_number | visits
        """
        with open(self.log_file_path, 'r') as log_file:
            current_file = None
            for line in log_file:
                line = line.strip()

                if line.startswith('/'):
                    if current_file is not None:
                        self.files[current_file.filename] = current_file
                    current_file = File()
                    current_file.filename = line

                if line.startswith('|') or line.startswith('-'):
                    continue
                elif current_file is not None and len(line) > 0:
                    line_parts = line.split('|')
                    try:
                        line_number = int(line_parts[0].strip())
                    except ValueError:
                        continue
                    visits = line_parts[1].strip()
                    # Convert visits to a numeric value based on the suffix (k, M, B)
                    if visits.endswith('k'):
                        visits = float(visits[:-1]) * 1000
                    elif visits.endswith('M'):
                        visits = float(visits[:-1]) * 1000000
                    elif visits.endswith('G'):
                        visits = float(visits[:-1]) * 1000000000
                    elif visits.endswith('T'):
                        visits = float(visits[:-1]) * 1000000000000
                    elif visits.endswith('E'):
                        visits = float(visits[:-1]) * 1000000000000000
                    else:
                        visits = float(visits.strip() or 0)
                    if visits > 0:
                        if(current_file.lines[line_number] > 0):
                            print("Error: line {} in file {} has already been visited".format(line_number, current_file.filename))
                        current_file.lines[line_number] = visits

        if current_file is not None:
            self.files[current_file.filename] = current_file

    def unique_visits(self, libB, file_to_consider):
        unique = 0
        for filename in file_to_consider:
            found = False
            for fn, file in self.files.items():
                if filename.split('/')[-1] == fn.split('/')[-1]:
                    found = True
                    break
            if not found:
                # file not present in this lib
                continue
            found = False
            for filenameB, fileB in libB.files.items():
                if filename.split('/')[-1] == filenameB.split('/')[-1]:
                    d=file.unique_visits(fileB)
                    if d.total_visits() > 0 and False:
                        print(file.filename)
                        print(sorted(file.lines.keys()))
                        print(fileB.filename)
                        print(sorted(fileB.lines.keys()))
                        print(d.filename)
                        print("Unique lines")
                        print(sorted(d.lines.keys()))
                        print(unique)
                    unique += d.total_visits()
                    found = True
                    break
            # file is not found in other lib but was part of the file to
            # consider, counting every line touched.
            if not found and file.total_visits() > 0:
                unique += len(file.lines.keys())
                continue
        return unique
    
    def merge(self, libB):
        for filename, file in self.files.items():
            for filenameB, fileB in libB.files.items():
                if filename.split('/')[-1] == filenameB.split('/')[-1]:
                    file.merge(fileB)
        return self



def main():
    """
    Main function to calculate and print total visits and visits at line 10 for each file.
    """
    parser = argparse.ArgumentParser(description='Calculate unique coverage for a folder.')
    parser.add_argument('--utopia_folder', type=str, help='Path to the folder containing coverage logs')
    parser.add_argument('--libfuzz_folder', type=str, help='Path to the folder containing coverage logs')
    parser.add_argument('--merge_iteration', type=bool, help='Merge the coverage of the different runs')
    args = parser.parse_args()

    
    utopia_coverage ={}
    libfuzz_coverage ={}
    target_folder = [args.utopia_folder, args.libfuzz_folder]
    for folder in target_folder:
        for target in os.listdir(folder):
            target_path = os.path.join(folder, target)
            runs = []
            for iteration in os.listdir(target_path):
                iteration_path = os.path.join(target_path, iteration)
                if os.path.isdir(iteration_path) and 'show' in os.listdir(iteration_path):
                    library_log_file_path = os.path.join(iteration_path, 'show')
                    runs.append(Library(library_log_file_path))

            if args.merge_iteration:
                for run in runs[1:]:
                    runs[0].merge(run)
            if folder == args.utopia_folder:
                utopia_coverage[target] = runs[0]
            elif folder == args.libfuzz_folder: 
                libfuzz_coverage[target] = runs[0]
    
    for common_target in sorted(set(utopia_coverage.keys()).intersection(set(libfuzz_coverage.keys()))):
        file_to_consider = libfuzz_coverage[common_target].get_all_files()
        unique_utopia = utopia_coverage[common_target].unique_visits(libfuzz_coverage[common_target], file_to_consider)
        unique_libfuzz = libfuzz_coverage[common_target].unique_visits(utopia_coverage[common_target], file_to_consider)
        print("Unique coverage for {} is utopia / libfuzz: {:10d} / {:10d}".format(common_target.ljust(15), unique_utopia, unique_libfuzz))
    

if __name__ == "__main__":
    main()
