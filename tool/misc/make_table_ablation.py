#!/usr/bin/env python3

import argparse
from prettytable import PrettyTable

def parse(report):
    s = {}

    with open(report) as f:
        lib = None
        for l in f:
            if not l.strip():
                continue

            row_arr = l.split(",")

            lib = row_arr[0]

            cov = float(row_arr[2].replace("%",""))

            covs = s.get(lib, [])

            covs.append(cov)

            s[lib] = covs

    s_norm = {}
    for lib, covs in s.items():
        s_norm[lib] = sum(covs) / len(covs)

    return s_norm

def win(tkn, a, b):
    an = float(a.replace("%",""))
    bn = float(b.replace("%",""))
    if an > bn:
        return f"\\textbf{{{tkn}}}"
    return tkn

def _main():
    parser = argparse.ArgumentParser(description='Produce table for ablation study')
    parser.add_argument('--field', '-f', help="Coverage results w/ field bias", required=True)
    parser.add_argument('--none', '-n', help="Coverage results w/o bias", required=True)

    args = parser.parse_args()
    
    field = args.field
    none = args.none

    field_s = parse(field)
    none_s = parse(none)

    # check if the keys are the same
    field_k = set(field_s.keys())
    none_k = set(none_s.keys())
    if field_k != none_k:
        print("[ERROR] Liberaries are not the same!")
        print("Field keys: ", field_k)
        print("None keys: ", none_k)
        exit(1)
    
    t = PrettyTable(['Library', 'w/o field bias', 'full liberator', 'delta'])
    for lib in sorted(field_s.keys()):
        f = field_s[lib]
        n = none_s[lib]
        d = f-n

        t.add_row([lib, f"{n}%", f"{f}%", f"{d:.2f}%"])

    print(t)

    # print("end!")
    # from IPython import embed; embed(); exit(1)

if __name__ == "__main__":
    _main()