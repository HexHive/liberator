
#ifndef INCLUDE_PDOM_DOMINATORS_H_
#define INCLUDE_PDOM_DOMINATORS_H_

#include "GenericDominatorTy.h"


class PostDominator : public GenericDominatorTy {
    protected:
        FunExitICFGNode* exit_node;
        IBBGraph::IBBNodeSet behind(IBBEdge*);
        void buildDom();

    public:
        PostDominator(BVDataPTAImpl* pt, FunEntryICFGNode* fun_entry,
                        FunExitICFGNode* fun_exit, bool do_indirect_jumps): 
                        GenericDominatorTy(pt, do_indirect_jumps) {
            setEntryNode(fun_entry);
            setExitNode(fun_exit);
        }

        inline void setExitNode(FunExitICFGNode* fun_exit) {exit_node = fun_exit;}
        inline FunExitICFGNode* getExitNode() {return exit_node;}

        inline string getDomName() {return "PostDominator";}
        bool dominates(ICFGNode*, ICFGNode*);
};
    

#endif /* INCLUDE_PDOM_DOMINATORS_H_ */