import random

class Bias:
    def __init__(self):
        pass 
    
    def get_random_candidate(self, driver, candidate_api):
        return random.choice(candidate_api)