#include "PostDominators.h"

IBBGraph::IBBNodeSet PostDominator::behind(IBBEdge* edge) {
    IBBGraph::IBBNodeSet nodes;

    // outs() << "1.a) Phi: " << sizePhi() << "\n";
    // outs() << "1.a) Phi Inv: " << sizePhiInv() << "\n";

    // edge is not in R
    if (C_ibbg.find(edge) == C_ibbg.end() ) {
        // src node == TAIL
        IBBNode* tail_e = edge->getDstNode();
        nodes.insert(tail_e);
    }
    // edge is in R
    else {
        // src node == TAIL
        IBBNode* tail_e = edge->getDstNode();
        nodes.insert(tail_e);

        // ICFGEdge* call_edge = phi_inv[(RetCFGEdge*)edge];
        IBBEdge* call_edge = phi_ibb[edge];
        IBBNode* tail_e_inv = call_edge->getDstNode();
        nodes.insert(tail_e_inv);
    }

    return nodes;
}

void PostDominator::buildDom() {

    ICFG* icfg = getICFG();

    // ICFGNodeSet relevant_nodes = getRelevantNodes();
    IBBGraph::IBBNodeSet relevant_nodes = ibbg->getNodeAllocated();
    FunExitICFGNode* exit_node = getExitNode();
    IBBNode *exit_node_ibb = ibbg->getIBBNode(exit_node->getId());

    int tot_nodes = relevant_nodes.size();

    outs() << "[INFO] Building initial post-dom structure\n";

    // dominator of the start node is the start itself
    // Dom(n0) = {n0}
    // dom[exit_node].insert(exit_node);
    addDom(exit_node_ibb, exit_node_ibb);
    // dom[exit_node].insert(exit_node);

    int n_node = 0;
    double per_node;

    // for all other nodes, set all nodes as the dominators
    // for each n in N - {n0}
    for (auto node: relevant_nodes) {

        // ICFGNode* node = it->second;
        if (node == exit_node_ibb)
            continue;

        n_node++;

        // Dom(n) = N;
        setDom(node, relevant_nodes);

        per_node = ((double)n_node/(double)tot_nodes) * 100;
        outs() << "[DOING] " << n_node << "/" << tot_nodes << 
                    " (" << per_node  << ")% \r";
    }

    outs() << "\n";

    outs() << "[INFO] Running real post-dom computation\n";

    IBBGraph::IBBNodeSet curr_inter; 
    IBBGraph::IBBNodeSet all_doms_behind;
    IBBGraph::IBBNodeSet last_inter;
    IBBGraph::IBBNodeSet new_dom;

    int n_iteration = 1;

    bool debug = false;
    bool is_changed = true;
    // iteratively eliminate nodes that are not dominators
    // while changes in any Dom(n)
    while (is_changed) {
        is_changed = false;

        outs() << "[DOING] Iteration " << n_iteration << "\n";
        n_iteration++;

        n_node = 1;

        std::set<IBBNode*>::reverse_iterator rit;

        // for each n in N - {n0}:
        for (rit = relevant_nodes.rbegin(); rit != relevant_nodes.rend(); rit++) {
            auto node = *rit;
        
            per_node = ((double)n_node/(double)tot_nodes) * 100;
            outs() << "[DOING] " << n_node << "/" << tot_nodes << 
                    " (" << per_node  << ")% \r";
            n_node++;

            // ICFGNode* node = it->second;
            if (node == exit_node_ibb)
                continue;    

            if (debug) {
                outs() << "1) Phi: " << sizePhi() << "\n";
                outs() << "1) Phi Inv: " << sizePhiInv() << "\n";
            }

            // outs() << (node->toString()) << "\n";

            // debug = node->getId() == 20;   

            if (node->hasOutgoingEdge()) {
                // ICFGNodeSet ahead_nodes;

                IBBNode::const_iterator it2 = node->OutEdgeBegin();
                IBBNode::const_iterator eit2 = node->OutEdgeEnd();

                bool first_intersect = true;

                for (; it2 != eit2; ++it2) {

                    for (auto n: behind(*it2)) {
                        IBBGraph::IBBNodeSet a_dom_set = getDom(n);

                        for (auto d: a_dom_set) 
                            // DOUBLE CHECK!
                            // if (isARelevantNode(d))
                                all_doms_behind.insert(d);
                        
                        a_dom_set.clear();
                    }

                    if (first_intersect) {
                        last_inter = all_doms_behind;
                        first_intersect = false;
                    } else {
                        // last_inter = all_doms_behind;
                        std::set_intersection(
                            last_inter.begin(), last_inter.end(),
                            all_doms_behind.begin(), all_doms_behind.end(), 
                            std::inserter(curr_inter, curr_inter.begin()));
                        std::swap(last_inter, curr_inter);
                        curr_inter.clear();

                    }

                    all_doms_behind.clear();
                }

                new_dom = last_inter;
                last_inter.clear();

                // if (debug) {
                //     outs() << "New Post-DOM:\n";
                //     for (auto n: new_dom)
                //         outs() << n->getId() << " ";
                //     outs() << "\n";
                // }

            }
            
            new_dom.insert(node);

            if (getDom(node) != new_dom) {
                clearDom(node);
                setDom(node, new_dom);
                is_changed = true;
            }

            if (debug) {
                outs() << "2) Phi: " << sizePhi() << "\n";
                outs() << "2) Phi Inv: " << sizePhiInv() << "\n";
            }

            new_dom.clear();
        }

        outs() << "\n";
    }

}

bool PostDominator::dominates(ICFGNode *a, ICFGNode *b) {
    if (!is_created) {
        outs() << "[ERROR] " << getDomName() << " not created yet!\n";
        exit(1);
    }

    if (a == b)
        return true;

    // ICFGNodeSet dominators_b = getDom(b);
    // return dominators_b.find(a) != dominators_b.end();
    
    auto bb_a = ibbg->getIBBNode(a->getId());
    auto bb_b = ibbg->getIBBNode(b->getId());

    if (bb_a == bb_b) {

        IBBNode::ICFGNodeList list = bb_a->getICFGNodes();
        IBBNode::ICFGNodeList::reverse_iterator rit;
        
        // for each n in N - {n0}:
        for (rit = list.rbegin(); rit != list.rend(); rit++) {
        // for (auto n: bb_a->getICFGNodes()) {
            auto n = *rit;
            if (n == a)
                return true;
            if (n == b)
                return false;
        }

        assert(false && "Did not found either a nor b!");

    } else {
        IBBGraph::IBBNodeSet dominators_b = getDom(bb_b);
        return dominators_b.find(bb_a) != dominators_b.end();
    }

    // this to ensure a return point
    return false;
}
