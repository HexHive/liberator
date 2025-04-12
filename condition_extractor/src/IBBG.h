#ifndef INCLUDE_IBBG_H_
#define INCLUDE_IBBG_H_

#include "SVF-LLVM/LLVMUtil.h"
#include "Graphs/ICFG.h"
#include "Graphs/SVFG.h"
#include <Graphs/GenericGraph.h>
#include "WPA/Andersen.h"

#include "PhiFunction.h"

using namespace SVF;
using namespace llvm;
using namespace std;

// class IBBEdge;
class IBBNode;

// generic edge between IBB
typedef GenericEdge<IBBNode> IBBEdgeTy;
class IBBEdge : public IBBEdgeTy {
public:
    
    enum Kind
    {
        IntraCF, CallCF, RetCF,
    };


public:
    IBBEdge(IBBNode* s, IBBNode* d, GEdgeFlag k) : IBBEdgeTy(s,d,k)
    {
    }
    ~IBBEdge() {
    }

    /// Get methods of the components
    //@{
    inline bool isCallEdge() const
    {
        return getEdgeKind() == CallCF;
    }
    inline bool isRetEdge() const
    {
        return getEdgeKind() == RetCF;
    }
    inline bool isIntraEdge() const
    {
        return getEdgeKind() == IntraCF;
    }
    //@}

    /// Overloading operator << for dumping ICFG node ID
    //@{
    friend OutStream& operator<< (OutStream &o, const IBBEdge &edge)
    {
        o << edge.toString();
        return o;
    }
    //@}

    const std::string toString() const {
        std::string str;
        llvm::raw_string_ostream rawstr(str);
        rawstr << "IBBEdge ";
        if (isCallEdge())
            rawstr << "Call";
        if (isRetEdge())
            rawstr << "Ret";
        if (isIntraEdge())
            rawstr << "Intra";
        rawstr << ": " << getSrcID() << " to " << getDstID();
        return rawstr.str();
    }
    
};


// Inter-procedural Basic-Block
typedef GenericNode<IBBNode, IBBEdge> IBBNodeTy;
class IBBNode : public IBBNodeTy {
public:
    typedef std::vector<ICFGNode *> ICFGNodeList;

    enum Kind {Call, Ret, Intra};
protected:
    ICFGNodeList nodes;
public:
    IBBNode(NodeID i, Kind k = Intra) : IBBNodeTy(i, k)
    {

    }

    inline void addICFGNode(ICFGNode* icfg_node) { nodes.push_back(icfg_node); }
    inline ICFGNodeList &getICFGNodes() { return nodes; }
    inline unsigned int getNumberNodes() { return nodes.size(); }
    inline ICFGNode* getLastNode() { return nodes.back(); }
    inline ICFGNode* getFirstNode() { return nodes.front(); }

    /// Overloading operator << for dumping ICFG node ID
    //@{
    friend OutStream &operator<<(OutStream &o, const IBBNode &node)
    {
        o << node.toString();
        return o;
    }
    //@}

    const std::string toString() const {
        std::string str;
        llvm::raw_string_ostream rawstr(str);
        rawstr << "IBBNode " << getId() << "\n\n";

        for (auto n: nodes)
            rawstr << n->toString() << "\n";

        return rawstr.str();
    }

    // for std:set
    bool operator<(const IBBNode& rhs) const {
        if (nodes.size() < rhs.nodes.size()) 
            return true;
        if (nodes.size() > rhs.nodes.size()) 
            return false;

        for (int i = 0; i < nodes.size(); i++)
            if (nodes[i] == rhs.nodes[i])
                continue;
            else
                return nodes[i] < rhs.nodes[i];

        // If the two IBB has same number of ICFGNode
        // AND all the nodes are the same, then, the two
        // IBB are the same, so < returns false
        return false;
    }

    // // copy assignment operator
    // IBBNode& operator=(const IBBNode &rhs) {
    //     for (auto n: rhs.nodes)
    //         this->nodes.push_back(n);

    //     for (auto e: rhs.inedges)
    //         this->inedges.push_back(e);
        
    //     for (auto e: rhs.outedges)
    //         this->outedges.push_back(e);

    //     return *this;
    // };
};

class IBBGraph : public GenericGraph<IBBNode, IBBEdge>
{
public:
    typedef std::vector<ICFGNode *> ICFGNodeVec;
    typedef std::set<NodeID> NodeIDSet;
    typedef std::map<NodeID, IBBNode*> IBBMap;
    typedef std::set<IBBEdge *> IBBEdgeSet;
    typedef std::set<IBBNode *> IBBNodeSet;

    // also used for phi_inv
    typedef std::map<IBBEdge*, IBBEdge*> PHIFunIBB;

    // for dom on outside
    typedef std::map<IBBNode *, IBBNodeSet> IBBNodeMap;
protected:
    NodeIDSet node_id_allocated;
    IBBMap id_to_ibbnode;
public:
    IBBGraph() {}

    inline NodeIDSet getNodeIdAllocated() {return node_id_allocated;}
    inline IBBNodeSet getNodeAllocated() {
        IBBNodeSet all_nodes;
        for (auto el: id_to_ibbnode) {
            auto node_id = el.first;
            auto ibb_node = el.second;
            all_nodes.insert(ibb_node);
        }
        return all_nodes;
    }

    IBBNode* addIBBNode(ICFGNodeVec node_list, IBBNode::Kind kind);
    // void removeIBBNode(NodeID);
    IBBNode* getIBBNode(NodeID);
    IBBEdge* getIBBEdge(ICFGEdge*);
    bool hasIBBEdge(NodeID,NodeID);
};

namespace SVF
{
    template <>
    struct DOTGraphTraits<IBBGraph *> : public DOTGraphTraits<ICFG *>
    {

        typedef IBBNode NodeType;
        DOTGraphTraits(bool isSimple = false)
        {
        }

        /// Return name of the graph
        static std::string getGraphName(IBBGraph *d)
        {
            return "IBB Graph";
        }

        std::string getNodeLabel(NodeType *node, IBBGraph *graph)
        {
            return getSimpleNodeLabel(node, graph);
        }

        /// Return the label of an ICFG node
        static std::string getSimpleNodeLabel(NodeType *node, IBBGraph *)
        {
            return node->toString();
        }

        static std::string getNodeAttributes(NodeType *node, IBBGraph *)
        {

            std::string str;
            llvm::raw_string_ostream rawstr(str);

            if (node == nullptr) {
                rawstr << "color=black";
                return rawstr.str();
            }
            
            ICFGNode *first_node = node->getFirstNode();
            ICFGNode *last_node = node->getLastNode();
            unsigned int n_node = node->getNumberNodes();

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
                    llvm::outs() << node->toString() << "\n";
                    assert(false && "not sure how to color this node!");
                }
                
            }

            rawstr << "";

            return rawstr.str();
        }

        template <class EdgeIter>
        static std::string getEdgeAttributes(NodeType *, EdgeIter EI, 
                                            IBBGraph *)
        {

            IBBEdge* edge = *(EI.getCurrent());
            assert(edge && "No edge found!!");

            if (edge->isCallEdge()) {
                return "style=solid,color=red";
            }
            if (edge->isRetEdge()) {
                return "style=solid,color=blue";
            }
            if (edge->isIntraEdge()) {
                return "style=solid,color=black";
            }

            return "color=black";
        
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
    struct GenericGraphTraits<IBBNode *> : public GenericGraphTraits<SVF::GenericNode<IBBNode, IBBEdge> *>
    {
    };

    /// Inverse GraphTraits specializations for call graph node, it is used for inverse traversal.
    template <>
    struct GenericGraphTraits<Inverse<IBBNode *>> : public GenericGraphTraits<Inverse<SVF::GenericNode<IBBNode, IBBEdge> *>>
    {
    };

    template <>
    struct GenericGraphTraits<IBBGraph *> : public GenericGraphTraits<SVF::GenericGraph<IBBNode, IBBEdge> *>
    {
        typedef IBBNode *NodeRef;
    };

} // End namespace llvm


#endif /* INCLUDE INCLUDE_IBBG_H_ */
