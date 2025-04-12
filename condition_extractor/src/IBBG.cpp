#include "IBBG.h"

IBBNode* IBBGraph::addIBBNode(ICFGNodeVec node_list, IBBNode::Kind kind)
{
    if (node_list.empty())
        return nullptr;

    // maybe check if node_list conflicts with some other node?
    for (auto n: node_list) {
        if (node_id_allocated.find(n->getId()) != node_id_allocated.end()) {
            outs() << "[ERROR] This node is already in the IBBGraph: \n";
            outs() << n->toString() << "\n";
            abort();
        }
    }

    NodeID node_id = node_list[0]->getId();

    IBBNode *node = new IBBNode(node_id, kind);
    for (auto n: node_list) {
        node->addICFGNode(n);
        node_id_allocated.insert(n->getId());
        id_to_ibbnode[n->getId()] = node;
    }
    addGNode(node_id, node);
    return node;
}

IBBNode* IBBGraph::getIBBNode(NodeID id)
{
    auto alloc_it = node_id_allocated.find(id);
    if (alloc_it == node_id_allocated.end()) {
        std::string str;
        raw_string_ostream rawstr(str);
        rawstr << "ID "<< id << " not found in the IBBG graph!\n";
        assert(false && rawstr.str().c_str());
        // FLAVIO -- returning NULL is very wrong!
        // return nullptr; 
    }

    return id_to_ibbnode[id];
}

IBBEdge *IBBGraph::getIBBEdge(ICFGEdge *edge)
{
    ICFGNode *src_icfg = edge->getSrcNode();
    ICFGNode *dst_icfg = edge->getDstNode();

    IBBNode* src_ibb = getIBBNode(src_icfg->getId());
    IBBNode* dst_ibb = getIBBNode(dst_icfg->getId());

    // do src_ibb connect dst_ibb?
    IBBEdge* call_edge_ibb = nullptr;

    IBBNode::const_iterator it, eit;
    it = src_ibb->OutEdgeBegin();
    eit = src_ibb->OutEdgeEnd();
    for (; it!=eit; ++it) {
        auto out_edge = *it;
        if (out_edge->getDstNode() == dst_ibb) {
            call_edge_ibb = out_edge;
            break;
        }
    }

    if (call_edge_ibb == nullptr){
        outs() << edge->toString() << "\n";
        outs() << getIBBNode(edge->getSrcID())->toString() << "\n";
        outs() << getIBBNode(edge->getDstID())->toString() << "\n";
    }
    assert(call_edge_ibb  && "IBB Call Edge not found!");
    // assert(call_edge_ibb->isIntraEdge()  && "IBB Edge is not a call edge!");

    return call_edge_ibb;
}

bool IBBGraph::hasIBBEdge(NodeID src, NodeID dst)
{
    IBBNode* src_ibb = getIBBNode(src);
    IBBNode* dst_ibb = getIBBNode(dst);

    // do src_ibb connect dst_ibb?
    IBBEdge* call_edge_ibb = nullptr;

    IBBNode::const_iterator it, eit;
    it = src_ibb->OutEdgeBegin();
    eit = src_ibb->OutEdgeEnd();
    for (; it!=eit; ++it) {
        auto out_edge = *it;
        if (out_edge->getDstNode() == dst_ibb) {
            call_edge_ibb = out_edge;
            break;
        }
    }

    if (call_edge_ibb)
        return true;
    else
        return false;
}
