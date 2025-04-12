#!/usr/bin/python3

import os, argparse, subprocess

def is_ok(line, allowed_files):
    
    record = line.split()

    if not record:
        return False
    
    file = record[0]

    if "/" in file:
        file = file.split("/")[-1]

    return file in allowed_files
        # print("is_ok")
        # from IPython import embed; embed()


def _main():
    parser = argparse.ArgumentParser(description='Calculate Coverage from Utopia reports')
    parser.add_argument('-reports', '-r', type=str, help='Report Files', required=True)
    parser.add_argument('-groundtruth', '-g', type=str, help='Ground Truth', required=True)
    parser.add_argument('-max', '-m', type=int, help='Number of Runs', required=True)
    
    args = parser.parse_args()

    reports = args.reports
    groundtruth = args.groundtruth
    max_run = args.max

    branch_gt = {}
    line_gt = {}
    ground_truth_files = {}
    for l in os.listdir(groundtruth):
        ground_truth_files[l] = set()
        branch_gt[l] = 0
        line_gt[l] = 0

    begin = "-"
    end = "Files which"

    for p in ground_truth_files.keys():
        filename = os.path.join(groundtruth, p, "iter_1", "report")
        with open(filename) as f:
            start_reading = False
            for l in f:
                if l.strip() == "":
                    continue
                if l.startswith(begin):
                    start_reading = True
                    continue
                if start_reading:
                    the_file = l.split()[0]
                    if l.startswith(end):
                        start_reading = False 
                        break
                    if "/" in the_file:
                        the_file = the_file.split("/")[-1]

                    l_arr = l.split()
                    branch = int(l_arr[10])
                    # miss_branch += int(l_arr[11])
                    line =  int(l_arr[7])
                    # miss_line += int(l_arr[8])


                    ground_truth_files[p].add(the_file)
                    branch_gt[p] += branch
                    line_gt[p] += line

    projects_drivers = {}

    AGGREGATE = "zzz#aggregate"

    for l in os.listdir(reports):
        # print(l)
        projects_drivers[l] = set()
        d = os.path.join(reports, l, "iter_1")
        for d in os.listdir(d):
            if d in ['functions', 'merged.profdata', 'report', 'show']:
                continue
            projects_drivers[l].add(d)
        projects_drivers[l].add(AGGREGATE)


    # from IPython import embed; embed(); exit(1)

    # # TODO: to remove, only for debug
    # CHECK = "minijail"
    # # max_run = 1
    leftover_files = set()
    result_str = set()

    for p, drvs in projects_drivers.items():
        # if p != CHECK:
        #     continue
        # print(filename)
        branch = 0
        line = 0
        for d in drvs:
            if d == AGGREGATE:
                continue

            branch = 0
            line = 0

            for i in range(1, max_run+1):
                filename = os.path.join(reports, p, f"iter_{i}", d, "report")
                with open(filename) as f:
                    for l in f:
                        if is_ok(l, ground_truth_files[p]):
                            l_arr = l.split()
                            branch_tot = int(l_arr[10])
                            miss_branch = int(l_arr[11])
                            branch += branch_tot - miss_branch

                            line_tot =  int(l_arr[7])
                            miss_line = int(l_arr[8])
                            line += line_tot - miss_line

                        else:
                            leftover_files.add(l)

            branch_trv = branch/max_run
            branch_per = branch_trv/branch_gt[p]

            line_trv = line/max_run
            lines_per = line_trv/line_gt[p]

            line_tot = line_gt[p]
            branch_tot = branch_gt[p]

            s = f"{p},{d},{line_trv:.2f} ({lines_per:.2%}),{branch_trv:.2f} ({branch_per:.2%})"
            result_str.add(s)
            # print(f"{p},{i},{lines_per:.2%},{branches_per:.2%}")

        
        branch = 0
        line = 0

        for i in range(1, max_run+1):
            filename = os.path.join(reports, p, f"iter_{i}", "report")
            with open(filename) as f:
                for l in f:
                    if is_ok(l, ground_truth_files[p]):
                        l_arr = l.split()
                        branch_tot = int(l_arr[10])
                        miss_branch = int(l_arr[11])
                        branch += branch_tot - miss_branch

                        line_tot =  int(l_arr[7])
                        miss_line = int(l_arr[8])
                        line += line_tot - miss_line

                    else:
                        leftover_files.add(l)

        branch_trv = branch/max_run
        branch_per = branch_trv/branch_gt[p]

        line_trv = line/max_run
        lines_per = line_trv/line_gt[p]

        line_tot = line_gt[p]
        branch_tot = branch_gt[p]

        s = f"{p},{AGGREGATE},{line_trv:.2f} ({lines_per:.2%}),{branch_trv:.2f} ({branch_per:.2%})"
        result_str.add(s)

    print("library,driver,line_trv_avg,line_per,branch_trv_avg,branch_per")
    for r in sorted(result_str):
        print(r.replace(AGGREGATE, "Aggregate"))

    # for l in leftover_files:
    #     print(l)
        

if __name__ == "__main__":
    _main()
