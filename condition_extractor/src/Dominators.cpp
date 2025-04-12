#include "Dominators.h"

IBBGraph::IBBNodeSet Dominator::ahead(IBBEdge* edge) {
    IBBGraph::IBBNodeSet nodes;

    // edge is not in R
    if (R_ibbg.find(edge) == R_ibbg.end() ) {
        // src node == HEAD
        IBBNode* head_e = edge->getSrcNode();
        nodes.insert(head_e);
    }
    // edge is in R
    else {
        // src node == HEAD
        IBBNode* head_e = edge->getSrcNode();
        nodes.insert(head_e);

        IBBEdge* call_edge = phi_inv_ibb[edge];
        IBBNode* head_e_inv = call_edge->getSrcNode();
        nodes.insert(head_e_inv);
    }

    return nodes;
}

void Dominator::buildDom() {

    ICFG* icfg = getICFG();

    // ICFGNodeSet relevant_nodes = getRelevantNodes();
    IBBGraph::IBBNodeSet relevant_nodes = ibbg->getNodeAllocated();
    FunEntryICFGNode* entry_node = getEntryNode();
    IBBNode *entry_node_ibb = ibbg->getIBBNode(entry_node->getId());

    int tot_nodes = relevant_nodes.size();

    outs() << "[INFO] Building initial dom structure\n";

    // dominator of the start node is the start itself
    addDom(entry_node_ibb, entry_node_ibb);

    int n_node = 0;
    double per_node;

    // for all other nodes, set all nodes as the dominators
    // for each n in N - {n0}
    for (auto node: relevant_nodes) {

        if (node == entry_node_ibb)
            continue;

        n_node++;

        // Dom(n) = N;
        setDom(node, relevant_nodes);

        per_node = ((double)n_node/(double)tot_nodes) * 100;
        outs() << "[DOING] " << n_node << "/" << tot_nodes << 
                    " (" << per_node  << ")% \r";
    }

    outs() << "\n";

    outs() << "[INFO] Running real dom computation\n";
    
    IBBGraph::IBBNodeSet curr_inter; 
    IBBGraph::IBBNodeSet all_doms_ahead;
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

        // for each n in N - {n0}:
        // for (ICFG::iterator it = icfg->begin(); it != icfg->end(); it++) {
        for (auto node: relevant_nodes) {

            per_node = ((double)n_node/(double)tot_nodes) * 100;
            outs() << "[DOING] " << n_node << "/" << tot_nodes << 
                    " (" << per_node  << ")% \r";
            n_node++;

            // ICFGNode* node = it->second;
            if (node == entry_node_ibb)
                continue;    

            // outs() << (node->toString()) << "\n";

            // debug = node->getId() == 18;   

            if (debug) {
                outs() << "Old DOM:\n";
                for (auto n: getDom(node))
                    outs() << n->getId() << " ";
                outs() << "\n";
                outs() << "Incoming edges: " << node->hasIncomingEdge() << "\n";
                outs() << "\n";
            }

            if (node->hasIncomingEdge()) {

                IBBNode::const_iterator it2 = node->InEdgeBegin();
                IBBNode::const_iterator eit2 = node->InEdgeEnd();

                bool first_intersect = true;

                for (; it2 != eit2; ++it2) {

                    // ICFGNode *ahead_node;

                    for (auto n: ahead(*it2)) {
                        IBBGraph::IBBNodeSet a_dom_set = getDom(n);

                        for (auto d: a_dom_set) 
                            // DOUBLE CHECK!
                            // if (isARelevantNode(d))
                                all_doms_ahead.insert(d);
                        
                        a_dom_set.clear();
                    }

                    if (debug) {
                        IBBEdge* edge = *it2;
                        outs() << "parent:\n";
                        outs() << edge->getSrcNode()->toString();
                        outs() << "all_doms_ahead\n";
                        for (auto n: all_doms_ahead)
                            outs() << n->getId() << " ";
                        outs() << "\n";
                    }

                    if (first_intersect) {
                        last_inter = all_doms_ahead;
                        first_intersect = false;
                    } else {
                        // last_inter = all_doms_ahead;
                        std::set_intersection(
                            last_inter.begin(), last_inter.end(),
                            all_doms_ahead.begin(), all_doms_ahead.end(), 
                            std::inserter(curr_inter, curr_inter.begin()));
                        std::swap(last_inter, curr_inter);
                        curr_inter.clear();

                    }

                    all_doms_ahead.clear();
                }

                new_dom = last_inter;
                last_inter.clear();

                if (debug) {
                    outs() << "New DOM:\n";
                    for (auto n: new_dom)
                        outs() << n->getId() << " ";
                    outs() << "\n";
                }

            }
            
            new_dom.insert(node);

            if (getDom(node) != new_dom) {
                clearDom(node);
                setDom(node, new_dom);
                is_changed = true;
            }

            new_dom.clear();
        }

        outs() << "\n";
    }
}


bool Dominator::dominates(ICFGNode *a, ICFGNode *b) {
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

        for (auto n: bb_a->getICFGNodes()) {
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
