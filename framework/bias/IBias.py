import random

from typing import Union

from . import Bias
from constraints import ConditionManager
from driver.ir import ApiCall, PointerType
from driver.factory import Factory
from common import Api, FunctionConditionsSet

class IBias(Bias):
    def __init__(self, conditions: FunctionConditionsSet):
        super().__init__()
        
        self.condition_manager = ConditionManager.instance()
        self.conditions = conditions
    
    def get_random_candidate(self, driver, candidate_api):
        
        if driver is None or len(driver) == 0:
            
            candidate_api_new = []
            for api in candidate_api:
                    n_ast = self.calc_ast(api)
                    candidate_api_new += [(api, n_ast)]
                
            w = [ww for _, ww in candidate_api_new]
            candidate_api = [c for c, _ in candidate_api_new]
            r_api = random.choices(candidate_api, weights=w)[0] 
            return r_api
        
        else:
            
            last_apicall = driver[-1][0]
            
            last_apicall_ats = self.get_ast(last_apicall)
            
            # from IPython import embed; embed(); exit
            
            candidate_api_new = []
            for api in candidate_api:
                # n_ast = self.calc_ast(call_next)
                n_ast = self.get_ast(api)
                
                common_fields = 0
                for ct in n_ast.keys() & last_apicall_ats.keys():
                    common_fields += len(n_ast[ct] & last_apicall_ats[ct])                    
                
                candidate_api_new += [(api, common_fields)]
                
                
            w = [ww for _, ww in candidate_api_new]
            if sum(w) == 0:
                w = [1 for _, _ in candidate_api_new]
            candidate_api = [c for c, _ in candidate_api_new]
            r_api = random.choices(candidate_api, weights=w)[0] 
            return r_api
        
    def get_ast(self, api:  Union[Api, ApiCall]):
        
        if isinstance(api, Api):
            api_call = Factory.api_to_apicall(api)
        else:
            api_call = api
        
        get_cond = lambda x: self.conditions.get_function_conditions(x.function_name)
        
        fc = get_cond(api_call)
        
        ats = {}
        
        rt = api_call.ret_type
        if isinstance(rt, PointerType):
            rt = rt.get_base_type()
        ats[rt] = set([".".join([f"{f}" for f in at.fields]) for at in fc.return_at.ats.access_type_set])
        
        # ats += [len(fc.return_at.ats.access_type_set)]
        
        for a, arg_c in enumerate(fc.argument_at):
            # ats += [len(arg.ats.access_type_set)]
            at = api_call.arg_types[a]
            if isinstance(at, PointerType):
                at = at.get_base_type()
                
            t_fields = ats.get(at, set())
            t_fields |= set([".".join([f"{f}" for f in at.fields]) for at in arg_c.ats.access_type_set])
            ats[at] = t_fields 
            
        return ats
    
    def calc_ast(self, api_call):
        
        get_cond = lambda x: self.conditions.get_function_conditions(x.function_name)
        
        fc = get_cond(api_call)
        
        ats = list()
        
        ats += [len(fc.return_at.ats.access_type_set)]
        
        for arg in fc.argument_at:
            ats += [len(arg.ats.access_type_set)]
            
        return sum(ats)