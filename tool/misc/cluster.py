#!/usr/bin/env python3

from typing import Set, Tuple

import numpy as np
from sklearn.cluster import AffinityPropagation
from Levenshtein import distance as levenshtein_distance

from datetime import datetime, timedelta
import os, time

# Function to get the creation time of a file
def get_creation_time(file_name):
    return os.path.getctime(file_name)

def cluster_drivers(host_result_folder: str, selecting_time = None) -> Set[Tuple[str, str]]:
    make_key = lambda seq : "".join(seq)

    strings = []

    driver_info = dict()
    
    select_per_time = False
    if selecting_time is not None:
        # Get creation time of driver0
        creation_time_driver0 = get_creation_time(os.path.join(host_result_folder, "drivers", "driver0.cc"))
        driver0_creation_datetime = datetime.fromtimestamp(creation_time_driver0)

        # Define the 5 minutes window
        time_window = timedelta(seconds=selecting_time)

        select_per_time = True
        

    with open(os.path.join(host_result_folder, "paths_observed.txt"), 'r') as fp:
        for l in fp:
            la = l.strip().split(":")
            if la[2] != "POSITIVE":
                continue
            
            # note: double check the driver actually exists
            if not os.path.isfile(os.path.join(host_result_folder, "drivers", f"{la[0]}")):
                continue
            
            driver_name = la[0]
            api_seq = la[1].split(";")
            seeds = int(la[3])
            
            if select_per_time:
                driver_path = os.path.join(host_result_folder, "drivers", f"{driver_name}.cc")
                driver_creation_time = get_creation_time(driver_path)
                driver_creation_datetime = datetime.fromtimestamp(driver_creation_time)
                
                if driver_creation_datetime - driver0_creation_datetime >= time_window:
                    break
            
            key = make_key(api_seq)

            strings += [api_seq]
            driver_info[key] = (seeds, driver_name)
    
    n = len(strings)
    similarity_matrix = np.zeros((n, n))
    
    if n == 0:
        return set()

    for i in range(n):
        for j in range(n):
            if i != j:
                similarity_matrix[i, j] = -levenshtein_distance(strings[i], strings[j])
            else:
                similarity_matrix[i, j] = 0
                
    # Affinity Propagation clustering
    affinity_propagation = AffinityPropagation(affinity="precomputed", random_state=0)
    affinity_propagation.fit(similarity_matrix)

    champ_driver = set()

    # Display the results
    clusters = affinity_propagation.labels_
    for cluster_id in np.unique(clusters):
        cluster_info = []
        for string_id in np.where(clusters == cluster_id)[0]:
            key = make_key(strings[string_id])
            (n_seed, driver_name) = driver_info[key]
            cluster_info += [(n_seed, driver_name, strings[string_id])]
            # print(f"   {driver_name} {strings[string_id]}: {n_seed}")
            # break
            
        # I know, this can be done in a line...don't annoy please!
        for _, driver_name, api_seq in sorted(cluster_info, key=lambda tup: tup[0], reverse=True):
            # a_str = ";".join(a)
            # print(f"{cluster_id}|{driver_name}|{a_str}|{s}")
            champ_driver.add((driver_name, ";".join(api_seq)))
            break
        
    return champ_driver

# def _main():
    
#     parser = argparse.ArgumentParser(description='Cluster Driver')
#     parser.add_argument('-path',  type=str, help='Run generation in debug mode', required=True)

#     args = parser.parse_args()
    
#     paths = args.path
    
#     strings = []

#     driver_info = dict()

#     with open(paths, 'r') as fp:
#         for l in fp:
#             la = l.strip().split(":")
#             if la[2] != "POSITIVE":
#                 continue
            
#             driver_name = la[0]
#             api_seq = la[1].split(";")
#             seeds = int(la[3])
            
#             key = make_key(api_seq)

#             strings += [api_seq]
#             driver_info[key] = (seeds, driver_name)

#     print(f"num of strings {len(strings)}")

#     # from IPython import embed; embed(); exit(1)

#     # Compute the similarity matrix
#     n = len(strings)
#     similarity_matrix = np.zeros((n, n))

#     for i in range(n):
#         for j in range(n):
#             if i != j:
#                 similarity_matrix[i, j] = -levenshtein_distance(strings[i], strings[j])
#             else:
#                 similarity_matrix[i, j] = 0

#     # Affinity Propagation clustering
#     affinity_propagation = AffinityPropagation(affinity="precomputed", random_state=0)
#     affinity_propagation.fit(similarity_matrix)

#     # Display the results
#     clusters = affinity_propagation.labels_
#     for cluster_id in np.unique(clusters):
#         # print(f"Cluster {cluster_id}:")
#         cluster_info = []
#         for string_id in np.where(clusters == cluster_id)[0]:
#             key = make_key(strings[string_id])
#             (n_seed, driver_name) = driver_info[key]
#             cluster_info += [(n_seed, driver_name, strings[string_id])]
#             # print(f"   {driver_name} {strings[string_id]}: {n_seed}")
#             # break
            
#         for s, d, a in sorted(cluster_info, key=lambda tup: tup[0], reverse=True):
#             a_str = ";".join(a)
#             print(f"{cluster_id}|{d}|{a_str}|{s}")
#             break

# if __name__ == "__main__":
#     _main()
