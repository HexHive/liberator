import random

from . import Bias
from dependency import DependencyGraph
from common import Utils

class SBias(Bias):
    def __init__(self):
        super().__init__()
        
        self.seeds_per_apiseq = {}
        
    def get_random_candidate(self, driver, candidate_api):
        
        positive_weights = []
        unknown_weights = []
        
        for api in candidate_api:
            apiseq = Utils.calc_api_seq_str(driver, api)
            
            # if api_state == ApiSeqState.UNKNOWN or api_state is None: 
            if apiseq not in self.seeds_per_apiseq:
                unknown_weights += [api]
            # NOTE: n seeds -1 means a negative sequence
            elif self.seeds_per_apiseq[apiseq] != -1:
                n_seeds = self.calc_seeds(driver, api)
                positive_weights += [(api, n_seeds)]
            
        n_unk_weights = len(unknown_weights)
        n_pos_weights = len(positive_weights)
        
        if n_pos_weights > 0:
            
            # this was a test for biasing API func call, it was a failure
            # positive_weights = [(a, sigmoid(w)) for a, w in positive_weights]

            sum_pos_weights = sum([w for _, w in positive_weights])

            # prob_unkn = float(n_unk_weights)/(n_unk_weights+n_pos_weights)

            # sum_unk_weights = prob_unkn/(1.0-prob_unkn)*sum_pos_weights

            candidate_api_new = positive_weights
            for u in unknown_weights:
                candidate_api_new += [(u, sum_pos_weights/n_unk_weights)]

            w = [ww for _, ww in candidate_api_new]
            candidate_api = [c for c, _ in candidate_api_new]
            r_api = random.choices(candidate_api, weights=w)[0] 
            # self.dump_log(driver, candidate_api, w)
            return r_api
        else:
            w = [1 for _ in candidate_api]
            r_api = random.choices(candidate_api, weights=w)[0] 
            # self.dump_log(driver, candidate_api, w)
            return r_api
    
    def calc_seeds(self, driver, api_call):
        
        api_seq_str = Utils.calc_api_seq_str(driver, api_call)
        
        ok_seq = {}
        
        for seq, val in self.seeds_per_apiseq.items():
            if seq.startswith(api_seq_str): # and val[0] == ApiSeqState.POSITIVE:
                ok_seq[seq] = val
            
            
        # ok_seq_save = ok_seq
            
        while True:
            ok_seq_new = {}
            
            for s1, v1 in ok_seq.items():
                has_longer = False
                for s2, _ in ok_seq.items():
                    if s1 == s2: 
                        continue
                    
                    if s2.startswith(s1):
                        has_longer = True
                        break
                if not has_longer:
                    ok_seq_new[s1] = v1
                    
            # Fix point: I reach the minimum set
            if ok_seq.keys() == ok_seq_new.keys():
                break
            
            ok_seq = ok_seq_new
            
        # if len(ok_seq_save) >= 3:
        #     print("calc_seeds..")
        #     from IPython import embed; embed(); exit(1)
            
        n_seq = len(ok_seq)
        sum_seeds = sum([v for _, v in ok_seq.items()])
            
        return sum_seeds/n_seq
    
    def update_feedback(self, apiseq, feed):
        self.seeds_per_apiseq[apiseq] = feed