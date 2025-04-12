
#ifndef INCLUDE_DOM_DOMINATORS_H_
#define INCLUDE_DOM_DOMINATORS_H_

#include "GenericDominatorTy.h"

class Dominator : public GenericDominatorTy {
    private:
        IBBGraph::IBBNodeSet ahead(IBBEdge* edge);
        void buildDom();

    public:
        Dominator(BVDataPTAImpl* pt, FunEntryICFGNode *fun_entry, 
                bool do_indirect_jumps)
         : GenericDominatorTy(pt, do_indirect_jumps) {
            setEntryNode(fun_entry);
        }

        inline string getDomName() {return "Dominator";}
        bool dominates(ICFGNode*, ICFGNode*);

};

#endif /* INCLUDE_DOM_DOMINATORS_H_ */