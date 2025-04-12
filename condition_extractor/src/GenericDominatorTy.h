#ifndef INCLUDE_GENDOM_DOMINATORS_H_
#define INCLUDE_GENDOM_DOMINATORS_H_

#include "SVF-LLVM/LLVMUtil.h"
#include "Graphs/ICFG.h"
#include "Graphs/SVFG.h"
#include <Graphs/GenericGraph.h>
#include "WPA/Andersen.h"

#include "PhiFunction.h"
#include "IBBG.h"

using namespace SVF;
using namespace llvm;
using namespace std;

// class PostDominator;
class DomEdge;
class DomNode;

class GenericDominatorTy : public GenericGraph<DomNode, DomEdge>
{
public:
    typedef std::set<ICFGNode *> ICFGNodeSet;
    typedef std::set<ICFGEdge *> ICFGEdgeSet;
    typedef std::set<const SVFFunction *> SVFFunctionSet;
    typedef std::vector<ICFGNode *> ICFGNodeVec;
    typedef std::map<ICFGNode *, ICFGNodeSet> ICFGNodeMap;
    typedef std::map<ICFGNode *, ICFGNodeVec> ICFGNodeMapV;

protected:
    BVDataPTAImpl *point_to;
    FunEntryICFGNode *entry_node;
    // dom works for Dominator and Postdominator
    // ICFGNodeMap dom;
    // ICFGNodeMapV dom_v;
    IBBGraph::IBBNodeMap dom;

    // PHIFun: C -> R
    PHIFun phi;
    // PHIFunInv: R -> C
    PHIFunInv phi_inv;
    // // R: return edge set
    // ICFGEdgeSet R;
    // // C: call edge set
    // ICFGEdgeSet C;

    // PHIFun: C -> R for IBB
    IBBGraph::PHIFunIBB phi_ibb;
    // PHIFunInv: R -> C for IBB
    IBBGraph::PHIFunIBB phi_inv_ibb;

    // PHIFun: C -> R for IBB
    IBBGraph::IBBEdgeSet R_ibbg;
    // C: call edge set
    IBBGraph::IBBEdgeSet C_ibbg;

    // real graph where the dominator operates to
    IBBGraph *ibbg;

    // dumped edges from alternative entry points
    ICFGEdgeSet dumped_edges;

    // ICFGNodeSet relevant_nodes;
    // ICFGNodeSet default_nodes;

    bool is_created = false;

    bool include_indirect_jumps = false;

public:
    GenericDominatorTy(BVDataPTAImpl*, bool);
    ~GenericDominatorTy() {
        delete ibbg;
    }
    // Dump graph somehow
    void dumpTransRed(const std::string &file, bool simple = false);
    void dumpDom(const std::string &file);
    // Load the graph somehow
    void loadDom(const std::string &file);

    IBBNode * getNode(int node_id);

    inline FunEntryICFGNode *getEntryNode() { return entry_node; }
    inline void setEntryNode(FunEntryICFGNode *node) { entry_node = node; }
    inline BVDataPTAImpl *getPointToAnalysis() { return point_to; }
    inline SVFModule *getModule() { return point_to->getModule(); }
    inline PTACallGraph *getPTACallGraph() { return point_to->getPTACallGraph(); }
    inline ICFG *getICFG() { return point_to->getICFG(); }
    inline PTACallGraph *getCallGraph() { return point_to->getPTACallGraph(); }
    inline IBBGraph *getIBBGraph() {return ibbg;}
    inline void addDumpedEdge(ICFGEdge *edge) { dumped_edges.insert(edge); }
    inline ICFGEdgeSet &getDumpedEdge() { return dumped_edges; }

    inline size_t sizePhi() { return phi.size(); }
    inline size_t sizePhiInv() { return phi_inv.size(); }

    inline void setPhi(PHIFun a_phi) { phi = a_phi; }
    inline RetCFGEdge *getPhi(CallCFGEdge *call_edge)
    {
        return phi[call_edge];
    }
    inline void setPhiInv(PHIFunInv a_phi_inv)
    {
        phi_inv = a_phi_inv;
    }
    inline CallCFGEdge *getPhiInv(RetCFGEdge *ret_edge)
    {
        return phi_inv[ret_edge];
    }

    // inline void setRelevantNodes(ICFGNodeSet nodes)
    // {
    //     relevant_nodes = nodes;
    // }
    inline unsigned int getTotRelevantNodes()
    {
        return ibbg->getNodeIdAllocated().size();
    }
    inline bool isARelevantNode(IBBNode *node)
    {
        IBBGraph::IBBNodeSet relevant_nodes = ibbg->getNodeAllocated();
        return relevant_nodes.find(node) != relevant_nodes.end();
    }
    inline  IBBGraph::IBBNodeSet getRelevantNodes() { 
        return ibbg->getNodeAllocated();
    }

    // inline void addR(RetCFGEdge *ret_edge) { R.insert(ret_edge); }
    // inline void addC(CallCFGEdge *call_edge) { C.insert(call_edge); }

    inline void addRIBBG(IBBEdge *ret_edge) { R_ibbg.insert(ret_edge); }
    inline void addCIBBG(IBBEdge *call_edge) { C_ibbg.insert(call_edge); }

    // dom set/get
    inline void addDom(IBBNode *node, IBBNode *dom_node)
    {
        dom[node].insert(dom_node);
    }
    inline void setDom(IBBNode *node, IBBGraph::IBBNodeSet dom_nodes)
    {
        dom[node] = dom_nodes;
    }
    inline void clearDom(IBBNode *node)
    {
        dom[node].clear();
    }
    inline IBBGraph::IBBNodeSet getDom(IBBNode *node)
    {
        return dom[node];
    }

    inline void saveIBBGraph(std::string filename) {
        GraphPrinter::WriteGraphToFile(SVFUtil::outs(), filename, ibbg, false);
    }
    
    virtual inline string getDomName() = 0;
    virtual bool dominates(ICFGNode *, ICFGNode *) = 0;

    void createDom();

    void pruneUnreachableFunctions();
    void buildPhiFun();
    void inferSubGraph();

private:
    // void pruneUnreachableFunctions();
    // void buildPhiFun();
    // void inferSubGraph();
    // void buildR();
    void restoreUnreachableFunctions();

    void buildTransientReduction();
    int getLongestPath(int, int, int **, int);
    void topoSort(int, int *, stack<int> &, int **, int);

    // debug functions
    void printPhiFunction();
    void printPhiInvFunction();
    // void printR();
    // void printC();

    virtual void buildDom() = 0;
};

typedef GenericEdge<DomNode> DomEdgeTy;
class DomEdge : public DomEdgeTy
{

public:
    /// Constructor
    DomEdge(DomNode *s, DomNode *d) : DomEdgeTy(s, d, 0)
    {
    }
};

typedef GenericNode<DomNode, DomEdge> DomNodeTy;
class DomNode : public DomNodeTy
{

public:
    /// 1 kinds of Dom node
    enum DomNodeK
    {
        DomeNode
    };

public:
    /// Constructor
    DomNode(IBBNode *n) : DomNodeTy(n->getId(), DomNodeK::DomeNode)
    {
        node = n;
    }

    IBBNode *getIBBNode()
    {
        return node;
    }

    const std::string toString() const
    {
        if (node == nullptr)
        {
            std::string str;
            raw_string_ostream rawstr(str);
            rawstr << "DomNode " << getId();
            return rawstr.str();
        }

        return node->toString();
    }

private:
    IBBNode *node;
};

namespace SVF
{
    template <>
    struct DOTGraphTraits<GenericDominatorTy *> : public DOTGraphTraits<ICFG *>
    {

        typedef DomNode NodeType;
        DOTGraphTraits(bool isSimple = false)
        {
        }

        /// Return name of the graph
        static std::string getGraphName(GenericDominatorTy *d)
        {
            return d->getDomName();
        }

        std::string getNodeLabel(NodeType *node, GenericDominatorTy *graph)
        {
            return getSimpleNodeLabel(node, graph);
        }

        /// Return the label of an ICFG node
        static std::string getSimpleNodeLabel(NodeType *node, GenericDominatorTy *)
        {
            return node->toString();
        }

        static std::string getNodeAttributes(NodeType *node, GenericDominatorTy *)
        {
            if (node == nullptr)
            {
                std::string str;
                raw_string_ostream rawstr(str);
                rawstr << "color=black";
                return rawstr.str();
            }

            std::string str;
            raw_string_ostream rawstr(str);

            IBBNode *in_node = node->getIBBNode();

            ICFGNode *first_node = in_node->getFirstNode();
            ICFGNode *last_node = in_node->getLastNode();
            unsigned int n_node = in_node->getNumberNodes();

            if (n_node == 1) {
                if (SVFUtil::isa<IntraICFGNode>(first_node))
                {
                    rawstr << "color=black";
                } 
                else if (SVFUtil::isa<CallICFGNode>(first_node))
                {
                    rawstr << "color=red";
                }
                else if (SVFUtil::isa<RetICFGNode>(first_node))
                {
                    rawstr << "color=blue";
                }
            } else {

                bool has_intra = false;
                has_intra |= SVFUtil::isa<IntraICFGNode>(first_node);
                has_intra |= SVFUtil::isa<IntraICFGNode>(last_node);
                has_intra |= SVFUtil::isa<FunEntryICFGNode>(first_node);
                has_intra |= SVFUtil::isa<FunEntryICFGNode>(last_node);
                has_intra |= SVFUtil::isa<FunExitICFGNode>(first_node);
                has_intra |= SVFUtil::isa<FunExitICFGNode>(last_node);

                bool has_call = SVFUtil::isa<CallICFGNode>(last_node);
                bool has_ret = SVFUtil::isa<RetICFGNode>(first_node);

                if (has_intra && !has_call && !has_ret)
                {
                    rawstr << "color=black";
                }
                else if (has_intra && has_call && !has_ret)
                {
                    rawstr << "color=red";
                }
                else if (has_intra && !has_call && has_ret)
                {
                    rawstr << "color=blue";
                }
                else if (!has_intra && has_call && has_ret)
                {
                    rawstr << "color=purple";
                }
                else {
                    outs() << node->toString() << "\n";
                    assert(false && "not sure how to color this node!");
                }
                
            }

            rawstr << "";

            return rawstr.str();
        }

        template <class EdgeIter>
        static std::string getEdgeAttributes(NodeType *, EdgeIter EI,
                                             GenericDominatorTy *)
        {
            return "style=solid";
        }

        template <class EdgeIter>
        static std::string getEdgeSourceLabel(NodeType *, EdgeIter EI)
        {
            return "";
        }
    };
} // End namespace llvm

namespace SVF
{
    /* !
     * GraphTraits specializations for generic graph algorithms.
     * Provide graph traits for traversing from a constraint node using standard graph traversals.
     */
    template <>
    struct GenericGraphTraits<DomNode *> : public GenericGraphTraits<SVF::GenericNode<DomNode, DomEdge> *>
    {
    };

    /// Inverse GraphTraits specializations for call graph node, it is used for inverse traversal.
    template <>
    struct GenericGraphTraits<Inverse<DomNode *>> : public GenericGraphTraits<Inverse<SVF::GenericNode<DomNode, DomEdge> *>>
    {
    };

    template <>
    struct GenericGraphTraits<GenericDominatorTy *> : public GenericGraphTraits<SVF::GenericGraph<DomNode, DomEdge> *>
    {
        typedef DomNode *NodeRef;
    };

} // End namespace llvm

#endif /* INCLUDE_GENDOM_DOMINATORS_H_ */
