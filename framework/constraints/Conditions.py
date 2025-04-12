from typing import List, Set, Dict, Tuple, Optional

from driver.ir import Type, PointerType, Variable

from common import AccessTypeSet, AccessType, Access, ValueMetadata

class Conditions:
    # conditions that have WRITE or RET
    ats: AccessTypeSet
    is_array: bool
    is_malloc_size: bool
    is_file_path: bool
    len_depends_on: Variable
    setby_dependencies: List[Variable]
    is_initialized: bool
    
    def __init__(self, mdata: ValueMetadata):
        self.ats = AccessTypeSet()
        self.add_conditions(mdata.ats)
        self.is_array = mdata.is_array
        self.is_malloc_size = mdata.is_malloc_size
        self.is_file_path = mdata.is_file_path
        self.len_depends_on = None 
        self.setby_dependencies = None
        self.is_initialized = False

    def is_init(self):
        return self.is_initialized
    
    def set_init(self):
        # print("set_init")
        # from IPython import embed; embed(); exit(1)
        self.is_initialized = True

    def unset_init(self):
        # print("unset_init")
        # from IPython import embed; embed(); exit(1)
        self.is_initialized = False

    def get_sub_fields(self, f_prev):
        f_prev_len = len(f_prev)
        f_prev_sub = []
        for x in self.ats:
            if f_prev == x.fields[:f_prev_len]:
                f_prev_sub += [x.fields]
        return f_prev_sub
    
    def get_jolly_conditions(self):
        writes = set([at for at in self.ats if at.access in [Access.WRITE, Access.RETURN]])

        # those terminating with -1
        candidate_jollies = set()
        for cj in writes:
            if len(cj.fields) > 0 and cj.fields[-1] == -1:
                candidate_jollies.add(cj)

        subfield_candidate_jollies = {}

        for cj in candidate_jollies:
            subfield_candidate_jollies[cj] = cj.fields[:-1]

        for w in writes:
            fld = w.fields
            if len(fld) == 0:
                continue
            for cj, cj_sub in subfield_candidate_jollies.items():
                if (cj_sub == fld[:-1] and fld[-1] != -1 and 
                    cj in candidate_jollies):
                    candidate_jollies.remove(cj)

        return candidate_jollies

    def is_compatible_with(self, r_cond: ValueMetadata) -> bool:

        if self.is_file_path != r_cond.is_file_path:
            return False

        # NOTE: FLAVIO: fields comparison is a bullshit!  
        # this is a test to show that w/ field matching, we have good results
        # anyway (or even better)
        return True

        # if self.is_array != r_cond.is_array:
        if not (self.is_array >= r_cond.is_array):
            return False

        

        if self.is_malloc_size != r_cond.is_malloc_size:
            return False

        r_requirements = set()
        for at in r_cond.ats:
            
            if at.access != Access.READ:
                continue
            # I do not want jolly reads
            at_fld = at.fields
            if len(at_fld) != 0 and at_fld[-1] == -1:
                continue
            r_requirements.add(at)

        r_updates = set([at for at in r_cond.ats if at.access == Access.WRITE])
        
        jolly_conditions = self.get_jolly_conditions()

        matching_requirements = 0
        unmatching_requirements = set()

        to_remove = set()
        for r in r_requirements:
            for h in r_updates:
                if r.fields == h.fields:
                    to_remove.add(r)

        r_requirements = r_requirements.difference(to_remove)

        for r in r_requirements:
            req_found = False
            for h in self.ats:
                if r.fields == h.fields:
                    matching_requirements += 1
                    req_found = True
            
            if not req_found:
                unmatching_requirements.add(r)


        real_unmatched = set()

        for u in unmatching_requirements:
            f_prev = u.fields[:-1]

            if len(u.fields) > 0 and u.fields[-1] == -1:
                f_prev_len = len(f_prev)
                f_prev_sub = self.get_sub_fields(f_prev)
                if len(f_prev_sub) > 0:
                    matching_requirements += 1
            else:
                while True:
                    f_prev_len = len(f_prev)
                    f_prev_sub = self.get_sub_fields(f_prev)
                    if len(f_prev_sub) != 0:
                        if len(f_prev_sub) == 1 and f_prev_sub[0] == f_prev:
                            matching_requirements += 1
                            # print(f"ok {f_prev} for {u}")
                            break
                        else:
                            # print(f"break1 {u}")
                            real_unmatched.add(u)
                            break
                    elif f_prev_len == 0:
                        # print(f"break2 {u}")
                        real_unmatched.add(u)
                        break
                    else:
                        # print(f_prev)
                        f_prev = f_prev[:-1]
                        f_prev_len = len(f_prev)

        real_unmatched_2 = set()

        # TO REMOVE JOLLY CONDITIONS
        for un in real_unmatched:
            un_fld = un.fields
            if len(un_fld) == 0:
                continue
            none_matching = True
            for jc in jolly_conditions:
                jc_sub = jc.fields[:-1]
                jc_sub_len = len(jc_sub)
                if un_fld[:jc_sub_len] == jc_sub:
                    # print(f"{un} ok!")
                    matching_requirements += 1
                    none_matching = False
            if none_matching:
                real_unmatched_2.add(un)

        # if matching_requirements != len(r_requirements):
        #     print("OK FINE")
        #     from IPython import embed; embed(); exit(1)

        return matching_requirements == len(r_requirements)

    def add_conditions(self, r_ats: AccessTypeSet):
        # I accumulate only WRITE and RET conditions
        holding_condition = set([at for at in r_ats if at.access == Access.WRITE])
        new_ats = AccessTypeSet(holding_condition)

        self.ats = self.ats.union(new_ats)

    @staticmethod
    def is_unconstraint(cond: ValueMetadata) -> bool:

        for at in cond.ats:
            if at.access == Access.READ and at.fields == []:
                continue
            elif at.access == Access.READ and at.fields == [-1]:
                continue
            elif at.access == Access.RETURN:
                continue
            elif at.access == Access.WRITE:
                continue
            else:
                return False
        
        return True

        # OLD VERSION, NOT CORRECT
        # if len(cond.ats) == 0:
        #     return True 
            
        # if len(cond.ats) == 1:
        #     at = list(cond.ats)[0]
        #     if at.access == Access.READ and at.fields == []:
        #         return True

        # return False
