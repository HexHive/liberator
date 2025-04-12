import random

from . import Bias
from constraints import ConditionManager
from driver.ir import ApiCall, PointerType
from driver.factory import Factory
from common import Api, FunctionConditionsSet

class FBias(Bias):
    def __init__(self, conditions: FunctionConditionsSet):
        super().__init__()
        
        self.condition_manager = ConditionManager.instance()
        self.conditions = conditions
    
    def get_random_candidate(self, driver, candidate_api):
        
        candidate_api_new = []
        for api in candidate_api:
            n_ast = self.calc_ast(api)
            candidate_api_new += [(api, n_ast)]
            
        w = [ww for _, ww in candidate_api_new]
        candidate_api = [c for c, _ in candidate_api_new]
        r_api = random.choices(candidate_api, weights=w)[0] 
        # self.dump_log(driver, candidate_api, w)
        return r_api
    
    def calc_ast(self, api_call):
        
        get_cond = lambda x: self.conditions.get_function_conditions(x.function_name)
        
        fc = get_cond(api_call)
        
        ats = list()
        
        ats += [len(fc.return_at.ats.access_type_set)]
        
        for arg in fc.argument_at:
            ats += [len(arg.ats.access_type_set)]
            
        return sum(ats)