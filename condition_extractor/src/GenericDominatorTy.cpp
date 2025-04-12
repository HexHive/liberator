#include "GenericDominatorTy.h"
#include "PhiFunction.h"

#include "SVF-LLVM/LLVMUtil.h"

// FLAVIO: I intentionally left the burned of creating the Dom relation in a
// separate function. I did not want to do everything in the constructor 
void GenericDominatorTy::createDom() {

    if (is_created) {
        outs() << "[ERROR] already created!\n";
        return;
    }

    outs() << "[INFO] Running pruneUnreachableFunctions()\n";
    this->pruneUnreachableFunctions();
    outs() << "[INFO] Running buildPhiFun()\n";
    this->buildPhiFun();
    outs() << "[INFO] Running inferSubGraph()\n";
    this->inferSubGraph();
    // outs() << "[INFO] Running buildR()\n";
    // this->buildR();
    outs() << "[INFO] Running buildDom()\n";
    this->buildDom();
    outs() << "[INFO] Running restoreUnreachableFunctions()\n";
    this->restoreUnreachableFunctions();

    is_created = true;

}

void GenericDominatorTy::restoreUnreachableFunctions() {
    // outs() << "[INFO] Restore eddges\n";
    for (auto edge: this->getDumpedEdge()) {
        // outs() << edge->toString() << "\n";
        edge->getDstNode()->addIncomingEdge(edge);
        edge->getSrcNode()->addOutgoingEdge(edge);
    }

    // UNCOMMENT FOR DEBUG
    // icfg->dump("icfg_restored");
}


void GenericDominatorTy::buildPhiFun() {

    SVFModule *svfModule = this->getModule();
    ICFG *icfg = this->getICFG();

    PHIFun phi;
    PHIFunInv phi_inv;

    getPhiFunction(svfModule, icfg, &phi, &phi_inv);    

    this->setPhi(phi);
    this->setPhiInv(phi_inv);

    // NOTE: to uncomment for debug
    // this->printPhiFunction();
    // this->printPhiInvFunction();
    // exit(1);

}

// void GenericDominatorTy::buildR() {

//     SVFModule *svfModule = this->getModule();
//     ICFG* icfg = this->getICFG();

//     SVF::SVFModule::llvm_iterator it = svfModule->llvmFunBegin();SVF::SVFModule::llvm_iterator eit = svfModule->llvmFunEnd();

//     for (;it != eit; ++it) {
//         const SVFFunction *fun = svfModule->getSVFFunction(*it);
//         // outs() << fun->getName() << " [in DOM]\n";
//         RetCFGEdge* ret_edge;
//         CallCFGEdge* call_edge;
//         ICFGNode::const_iterator it_fun_exit, eit_fun_exit;
//         ICFGNode::const_iterator it_fun_entry, eit_fun_entry;

//         FunExitICFGNode *fun_exit = icfg->getFunExitICFGNode(fun);
//         FunEntryICFGNode *fun_entry = icfg->getFunEntryICFGNode(fun);

//         if (fun_exit != nullptr) {
//             // outs() << "fun_exit: " << fun_exit->toString() << "\n";
            
//             it_fun_exit = fun_exit->OutEdgeBegin();
//             eit_fun_exit = fun_exit->OutEdgeEnd();
//             for (; it_fun_exit != eit_fun_exit; ++it_fun_exit) {
//                 // outs() << "it_fun_exit: " << (*it_fun_exit)->toString() << "\n";
//                 ret_edge = (RetCFGEdge*)(*it_fun_exit);
                
//                 this->addR(ret_edge);
//             }
//         }

//         if (fun_entry != nullptr) {
//             it_fun_entry = fun_entry->InEdgeBegin();
//             eit_fun_entry = fun_entry->InEdgeEnd();
//             for (; it_fun_entry != eit_fun_entry; ++it_fun_entry) {
//                 // outs() << "it_fun_exit: " << (*it_fun_exit)->toString() << "\n";
//                 call_edge = (CallCFGEdge*)(*it_fun_entry);
                
//                 this->addC(call_edge);
//             }
//         }

//     }

//     // NOTE: for debug
//     // this->printR();
//     // this->printC();
//     // exit(1);
// }

void GenericDominatorTy::pruneUnreachableFunctions() {

    assert(this->getEntryNode() && "We need an entry block!");

    const SVFFunction *main_fun = this->getEntryNode()->getFun();

    SVFModule *svfModule = this->getModule();
    PTACallGraph* callgraph = this->getPTACallGraph();

    SVF::SVFModule::const_iterator it, eit;

    SVFFunctionSet functions_done;

    bool uncalled_functions = true;
    while (uncalled_functions) {

        uncalled_functions = false;
        
        it = svfModule->begin();
        eit = svfModule->end();

        for (;it != eit; ++it) {
            const SVFFunction *fun = *it;

            ICFGEdgeSet tmp_dumped_edges;

            // outs() << "Fun: " << fun->getName() << "\n";

            if (fun == main_fun) {
                // outs() << "skip it\n";
                continue;
            }

            if (functions_done.find(fun) != functions_done.end())
                continue;

            FunEntryICFGNode *fun_entry = this->getICFG()->getFunEntryICFGNode(fun);
            FunEntryICFGNode *entry_called;
            FunExitICFGNode *exit_called;
            PTACallGraphNode *node_callee, *node_called;

            if (!fun_entry->hasIncomingEdge()) {
                uncalled_functions = true;

                // outs() << "Has not incoming edges\n";
                node_callee = callgraph->getCallGraphNode(fun);

                if (node_callee->hasOutgoingEdge()) {
                    // outs() << "Has outgoing edges\n";

                    PTACallGraphNode::const_iterator it2, eit2;
                    it2 = node_callee->OutEdgeBegin();
                    eit2 = node_callee->OutEdgeEnd();

                    for (; it2 != eit2; ++it2) {
                        node_called = (*it2)->getDstNode();        
                        auto const fun_called = node_called->getFunction();

                        // outs() << fun_called->getName() << "\n";

                        ICFGEdge *edge_to_remove = nullptr;

                        // have to select the callee node in ICFG, before it was
                        // the calle in CF
                        entry_called = this->getICFG()
                                        ->getFunEntryICFGNode(fun_called);
                        ICFGNode::const_iterator it3 = 
                                        entry_called->InEdgeBegin();
                        ICFGNode::const_iterator eit3 = 
                                        entry_called->InEdgeEnd();
                        if (entry_called->hasIncomingEdge()) {
                            for (; it3 != eit3; ++it3) {
                                ICFGNode *src = (*it3)->getSrcNode();
                                if (src->getFun() == fun) {
                                    edge_to_remove = *it3;
                                    break;
                                }
                            }

                            assert(edge_to_remove &&
                                    "The call edge to remove is not found!");

                            tmp_dumped_edges.insert(edge_to_remove);
                        }

                        exit_called = this->getICFG()->getFunExitICFGNode(fun_called);
                        if (exit_called->hasOutgoingEdge()) {
                            edge_to_remove = nullptr;
                            it3 = exit_called->OutEdgeBegin();
                            eit3 = exit_called->OutEdgeEnd();
                            for (; it3 != eit3; ++it3) {
                                ICFGNode *dst = (*it3)->getDstNode();
                                if (dst->getFun() == fun) {
                                    edge_to_remove = *it3;
                                    break;
                                }
                            }

                            assert(edge_to_remove && 
                                    "The return edge to remove is not found!");

                            tmp_dumped_edges.insert(edge_to_remove);
                        }
                    }

                }

                // outs() << "[INFO] Edges to remove (tmp)\n";
                for (auto edge: tmp_dumped_edges) {
                    // outs() << edge->toString() << "\n";
                    edge->getDstNode()->removeIncomingEdge(edge);
                    edge->getSrcNode()->removeOutgoingEdge(edge);
                    // dumped_edges.insert(edge);str
                    this->addDumpedEdge(edge);
                }

                functions_done.insert(fun);
            }
        }
    }

    // this->getICFG()->dump("icfg_pruned");

    // outs() << "FUNCTIONS:\n";
    
    // for (auto f: functions_done)
    //     outs() << f->getName() << "\n";

    // outs() << "[END] Ends here for debug\n";
    // exit(1);
}


void GenericDominatorTy::inferSubGraph() {

    FunEntryICFGNode *entry_node = this->getEntryNode();

    assert(entry_node && "We need an entry block!");

    std::stack<PTACallGraphNode*> working;
    std::set<PTACallGraphNode*> visited;

    PTACallGraph* callgraph = getCallGraph();
    ICFG* icfg = getICFG();

    const SVFFunction *fun = entry_node->getFun();
    PTACallGraphNode *entry_fun = callgraph->getCallGraphNode(fun);

    SVFFunctionSet functions;

    working.push(entry_fun);
    functions.insert(fun);

    while(!working.empty()) {

        PTACallGraphNode* node = working.top();
        working.pop();

        if (visited.find(node) != visited.end())
            continue;

        if (node->hasOutgoingEdge()) {
            PTACallGraphNode::const_iterator it = node->OutEdgeBegin();
            PTACallGraphNode::const_iterator eit = node->OutEdgeEnd();
        
            for (; it != eit; ++it) {
                PTACallGraphEdge *edge = *it;

                if (edge->isDirectCallEdge() || 
                    (include_indirect_jumps && edge->isIndirectCallEdge())) {
                    PTACallGraphNode *dst_fun = edge->getDstNode();
                    functions.insert(dst_fun->getFunction());
                    working.push(dst_fun);
                }
            }
        }

        visited.insert(node);

    }

    // outs() << "Functions:\n";
    // for(auto f: functions)
    //     outs() << f->getName() << "\n";
    // outs() << "-> debug\n";
    // exit(1);

    // std::stack<ICFGNode*> working_n;
    // std::set<ICFGNode*> visited_n;

    // working_n.push(entry_node);

    // while(!working_n.empty()) {

    //     ICFGNode *node = working_n.top();
    //     working_n.pop();

    //     if (node->hasOutgoingEdge()) {
    //         ICFGNode::const_iterator it = node->OutEdgeBegin();
    //         ICFGNode::const_iterator eit = node->OutEdgeEnd();
        
    //         for (; it != eit; ++it) {
    //             ICFGEdge *edge = *it;
    //             ICFGNode *dst = edge->getDstNode();

    //             if (visited_n.find(dst) != visited_n.end())
    //                 continue;
                
    //             if(auto ret_edge = SVFUtil::dyn_cast<RetCFGEdge>(edge)) {
    //                 visited_n.insert(dst);
    //                 working_n.push(dst);
    //             } 
    //             else if(auto call_edge = SVFUtil::dyn_cast<CallCFGEdge>(edge)) {
    //                 ICFGEdge *next_ret = this->getPhi(call_edge);
    //                 ICFGNode *dst_r = next_ret->getDstNode();

    //                 ICFGNode *src = edge->getSrcNode();
    //                 bool is_call_indirect = false;
    //                 if (auto call_node = SVFUtil::dyn_cast<CallICFGNode>(src))
    //                     is_call_indirect = call_node->isIndirectCall();

    //                 if (is_call_indirect) {
    //                     working_n.push(dst_r);
    //                     visited_n.insert(dst_r);
    //                 } else {
    //                     working_n.push(dst);
    //                     working_n.push(dst_r);
    //                 }
    //                 visited_n.insert(dst);
    //             }
    //             else {
    //                 working_n.push(dst);
    //                 visited_n.insert(dst);
    //             }
    //         }
    //     }

    // }

    outs() << "[INFO] Building IBB graph\n";

    for (auto f: functions) {
        ICFGNodeSet visited2;
        std::stack<std::tuple<ICFGNode*,ICFGNodeVec, IBBNode::Kind>> working;
        ICFGNode* entry_node = icfg->getFunEntryICFGNode(f);
        ICFGNodeVec empty_node_list;
        working.push(std::make_tuple(entry_node, empty_node_list, 
            IBBNode::Kind::Intra));

        // outs() << "Fun " << f->getName() << " doing\n";

        while(!working.empty()) {
            auto el = working.top();
            working.pop();

            ICFGNode *node = std::get<0>(el);
            ICFGNodeVec node_list = std::get<1>(el);
            IBBNode::Kind ibb_kind = std::get<2>(el);

            unsigned int n_outgoingedges = 0;
            unsigned int n_incomingedges = 0;
            ICFGNode::const_iterator it = node->OutEdgeBegin();
            ICFGNode::const_iterator eit = node->OutEdgeEnd();        
            for (; it != eit; ++it)
                n_outgoingedges++;

            it = node->InEdgeBegin();
            eit = node->InEdgeEnd();        
            for (; it != eit; ++it)
                n_incomingedges++;

            // if (node->getId() == 7185) {
                
            //     outs() << "[DEBUG] this is unreachable\n";
            //     outs() << node->toString() << "\n";
            //     outs() << "incoming edges: " << n_incomingedges << "\n";
            //     outs() << "outcoming edges: " << n_outgoingedges << "\n";

            //     it = node->InEdgeBegin();
            //     eit = node->InEdgeEnd();        

            //     for (; it != eit; ++it) {
            //         auto edge = *it;
            //         auto src = edge->getSrcNode();
            //         outs() << src->toString() << "\n";
            //     }

            //     exit(1);
            // }

            if (visited2.find(node) != visited2.end()) {
                // outs() << "[DEBUG] Node already visited, store and skip\n";
                // outs() << node->toString() << "\n";
                ibbg->addIBBNode(node_list, ibb_kind);
                continue;
            }

            // I explore only inside the function
            if (SVFUtil::isa<FunExitICFGNode>(node)) {
                node_list.push_back(node);
                ibbg->addIBBNode(node_list, IBBNode::Kind::Ret);
                continue;
            }

            if (auto n_call = SVFUtil::dyn_cast<CallICFGNode>(node)) {
                node_list.push_back(node);
                
                IBBNode* ibb_node = ibbg->addIBBNode(
                    node_list, IBBNode::Kind::Call);

                if (ibb_node == nullptr) {
                    outs() << "[DEBUG] this node has not predecessors:\n";
                    outs() << node->toString() << "\n";
                    assert(false);
                }

                RetICFGNode* n_ret = const_cast<RetICFGNode*>
                                (n_call->getRetICFGNode());
                auto p = std::make_tuple(n_ret, empty_node_list,       
                    IBBNode::Kind::Ret);
                working.push(p);
                continue;
            } else if (n_outgoingedges == 1 && n_incomingedges == 1) {
                ICFGEdge *edge = *node->OutEdgeBegin();
                ICFGNode *dest_node = edge->getDstNode();
                node_list.push_back(node);

                auto p = std::make_tuple(dest_node, node_list, ibb_kind);
                working.push(p);
            } else  if (n_outgoingedges == 0) {
                node_list.push_back(node);
                ibbg->addIBBNode(node_list, ibb_kind);
            } else {
                ICFGNodeVec new_node_list;
                if (n_incomingedges == 1)
                    node_list.push_back(node);
                else
                    new_node_list.push_back(node);
                ibbg->addIBBNode(node_list, ibb_kind);

                it = node->OutEdgeBegin();
                eit = node->OutEdgeEnd();        
                for (; it != eit; ++it) {
                    ICFGEdge *edge = *it;
                    ICFGNode *dest_node = edge->getDstNode();
                    auto p = std::make_tuple(dest_node, 
                                new_node_list, ibb_kind);
                    working.push(p);
                }
            } 

            visited2.insert(node);

        }

        // outs() << "Fun " << f->getName() << " done\n";
    }

    // outs() << "[DEBUG] Adding edges to IBB Graph\n";
    IBBGraph::NodeIDSet nodes_allocated = ibbg->getNodeIdAllocated();

    IBBGraph::iterator it = ibbg->begin();
    IBBGraph::iterator eit = ibbg->end();
    for (;it != eit; ++it) {
        auto el = *it;
        auto node = el.second;
        
        auto first_ist = node->getFirstNode();
        auto last_ist = node->getLastNode();

        bool go_default_branch = true;
        if (!include_indirect_jumps) {
            if (auto call_ist = SVFUtil::dyn_cast<CallICFGNode>(last_ist)) {
                if (call_ist->isIndirectCall()) {

                    auto ret_inst = call_ist->getRetICFGNode();
                    auto ret_inst_id = ret_inst->getId();
                    auto next_bb = ibbg->getIBBNode(ret_inst_id);

                    auto edge_kind = IBBEdge::Kind::IntraCF;
                    IBBEdge* edge = new IBBEdge(node, next_bb, edge_kind);
                    edge->getDstNode()->addIncomingEdge(edge);
                    edge->getSrcNode()->addOutgoingEdge(edge);

                    go_default_branch = false;
                }
            }
        }

        // outs() << "node: " << node->toString() << "\n";

        if (go_default_branch) {
            ICFGNode::const_iterator it = last_ist->OutEdgeBegin();
            ICFGNode::const_iterator eit = last_ist->OutEdgeEnd();
            for (; it != eit; ++it) {
                ICFGEdge *e = *it;
                ICFGNode *dest_node = e->getDstNode();
                auto dest_node_id = dest_node->getId();

                auto it_found = nodes_allocated.find(dest_node_id);
                if (it_found == nodes_allocated.end()) 
                    continue;

                // outs() << "out: " << dest_node->toString() << "\n";
                auto next_bb = ibbg->getIBBNode(dest_node_id);

                auto edge_kind = IBBEdge::Kind::IntraCF;
                if (isa<CallCFGEdge>(e))
                    edge_kind = IBBEdge::Kind::CallCF;
                if (isa<RetCFGEdge>(e))
                    edge_kind = IBBEdge::Kind::RetCF;

                IBBEdge* edge = new IBBEdge(node, next_bb, edge_kind);
                edge->getDstNode()->addIncomingEdge(edge);
                edge->getSrcNode()->addOutgoingEdge(edge);

                if (edge->isCallEdge())
                    addCIBBG(edge);
                if (edge->isRetEdge())
                    addRIBBG(edge);
            }
        }
    }

    // outs() << "debug add edges\n";
    // exit(1);

    // outs() << "[DEBUG] Print C\n";
    // for (auto e: C) {
    //     outs() << e->toString() << "\n";
    // }

    // outs() << "[DEBUG] Print R\n";
    // for (auto e: R) {
    //     outs() << e->toString() << "\n";
    // }

    // convert Phi/PhiInv to PhiIBB/PhiInvIBB    
    for (auto el: phi) {
        auto call_edge = el.first;
        auto ret_edge = el.second;

        auto end_node = nodes_allocated.end();

        auto it_call_src_id = nodes_allocated.find(call_edge->getSrcID());
        auto it_call_dst_id = nodes_allocated.find(call_edge->getDstID());
        auto it_ret_src_id = nodes_allocated.find(ret_edge->getSrcID());
        auto it_ret_dst_id = nodes_allocated.find(ret_edge->getDstID());

        if (it_call_src_id == end_node ||
            it_call_dst_id == end_node ||
            it_ret_src_id == end_node ||
            it_ret_dst_id == end_node)
            continue;

        // this generates more problems
        // if (!hasIBBEdge(*it_call_src_id, *it_call_dst_id) || 
        //     !hasIBBEdge(*it_ret_src_id, *it_ret_dst_id))
        //     continue;

        auto call_edge_ibb = ibbg->getIBBEdge(call_edge);
        auto ret_edge_ibb = ibbg->getIBBEdge(ret_edge);

        phi_ibb[call_edge_ibb] = ret_edge_ibb;
    }

    // outs() << "[INFO] Print PHI IBB\n";
    // for (auto el: phi_ibb) {
    //     outs() << "phi:\n";
    //     outs() << el.first->toString() << "\n";
    //     outs() << el.second->toString() << "\n";
    //     outs() << "\n";
    // }
    
    // phi_inv_ibb
    for (auto el: phi_inv) {
        auto ret_edge = el.first;
        auto call_edge = el.second;

        auto end_node = nodes_allocated.end();

        auto it_call_src_id = nodes_allocated.find(call_edge->getSrcID());
        auto it_call_dst_id = nodes_allocated.find(call_edge->getDstID());
        auto it_ret_src_id = nodes_allocated.find(ret_edge->getSrcID());
        auto it_ret_dst_id = nodes_allocated.find(ret_edge->getDstID());

        if (it_call_src_id == end_node ||
            it_call_dst_id == end_node ||
            it_ret_src_id == end_node ||
            it_ret_dst_id == end_node)
            continue;

        // this generates more problems
        // if (!hasIBBEdge(*it_call_src_id, *it_call_dst_id) || 
        //     !hasIBBEdge(*it_ret_src_id, *it_ret_dst_id))
        //     continue;

        auto call_edge_ibb = ibbg->getIBBEdge(call_edge);
        auto ret_edge_ibb = ibbg->getIBBEdge(ret_edge);

        phi_inv_ibb[ret_edge_ibb] = call_edge_ibb;
    }
     
    // outs() << "[INFO] Print PHI INV IBB\n";
    // for (auto el: phi_inv_ibb) {
    //     outs() << "phi inv:\n";
    //     outs() << el.first->toString() << "\n";
    //     outs() << el.second->toString() << "\n";
    //     outs() << "\n";
    // }

    // NodeIDSet icfg_node_id;
    // for (auto n: this->getRelevantNodes())
    //     icfg_node_id.insert(n->getId());

    // NodeIDSet intersection;
    // NodeIDSet ibbg_missing;
    // NodeIDSet ibbg_inpiu;

    // std::set_intersection(
    // icfg_node_id.begin(), icfg_node_id.end(),
    // node_id_allocated.begin(), node_id_allocated.end(), 
    // std::inserter(intersection, intersection.begin()));

    // for (auto n : icfg_node_id) {
    //     if (intersection.find(n) == intersection.end())
    //         ibbg_missing.insert(n);
    // }

    // for (auto n : node_id_allocated) {
    //     if (intersection.find(n) == intersection.end())
    //         ibbg_inpiu.insert(n);
    // }

    // outs() << "[INFO] ICFG Interesting nodes " << icfg_node_id.size() << "\n";
    // outs() << "[INFO] IBBG Interesting nodes " << node_id_allocated.size() << "\n";
    // outs() << "[INFO] Intersection " << intersection.size() << "\n";
    // outs() << "[INFO] ICFG missing\n";
    // for (auto id: ibbg_missing) {
    //     auto n = getICFG()->getICFGNode(id);
    //     outs() << n->toString() << "\n";
    // }

    // outs() << "[INFO] IBBG additional nodes " << ibbg_inpiu.size() << "\n";
    // int upperbound = 20;
    // for (auto id: ibbg_inpiu) {
    //     auto n = getICFG()->getICFGNode(id);
    //     outs() << n->toString() << "\n";
    //     if (upperbound-- <= 0)
    //         break;
    // }
    // ICFG* icfg = this->getICFG();
    // outs() << "[INFO] All nodes " << icfg->getTotalNodeNum() << "\n";
    // for (auto n: visited) {
    //     outs() << n->toString() << "\n";
    //     outs() << n->getNodeKind() << "\n";
    // }

    // outs() << "Print IBB graph for debug\n";
    // saveIBBGraph("ibbgraph_3");

    // outs() << "Exit for debug\n";
    // exit(1);
}

GenericDominatorTy::GenericDominatorTy(BVDataPTAImpl* a_point_to,
                    bool do_indirect_jumps)
{
    include_indirect_jumps = do_indirect_jumps;
    point_to = a_point_to;

    PTACallGraph* callgraph = point_to->getPTACallGraph();
    ICFG *icfg = point_to->getICFG();
    icfg->updateCallGraph(callgraph);

    ibbg = new IBBGraph();
}

/*!
 * Dump DOMINATOR graph!
 */
void GenericDominatorTy::dumpTransRed(const std::string& file, bool simple)
{
    if (!is_created) {
        outs() << "[ERROR] " << getDomName() << " not created yet!\n";
        exit(1);
    }

    outs() << "[INFO] Dom covering " << getTotRelevantNodes() << "\n";
    outs() << "[INFO] Running transient reduction...\n";
    outs() << "[INFO] This might take a while..." 
            << "if too long, kill the process\n";

    buildTransientReduction();
    GraphPrinter::WriteGraphToFile(SVFUtil::outs(), file, this, simple);
}

void GenericDominatorTy::dumpDom(const std::string& file)
{
    if (!is_created) {
        outs() << "[ERROR] " << getDomName() << " not created yet!\n";
        exit(1);
    }

    outs() << "[INFO] Dom covering " << getTotRelevantNodes() << "\n";
    outs() << "[INFO] This might take a while..." 
            << "if too long, kill the process\n";

    IBBGraph::IBBNodeSet relevant_nodes = ibbg->getNodeAllocated();
    ofstream dump_file;
    dump_file.open (file);
    for (auto d: relevant_nodes) {
        dump_file << d->getId() << " ";

        int n_dom = dom[d].size();
        int j = 0;

        for (auto n: dom[d]) {
            dump_file << n->getId();
            if (j < n_dom - 1)
                dump_file << " ";
            j++;
        }

        dump_file << "\n";
    }
    dump_file.close();

}

void GenericDominatorTy::loadDom(const std::string &file) {
    if (is_created) {
        outs() << "[ERROR] " << getDomName() << " is already created!\n";
        exit(1);
    }

    outs() << "[INFO] Loading " << file << "\n";
    outs() << "[INFO] This might take a while..." 
            << "if too long, kill the process\n";

    outs() << "[INFO] Running pruneUnreachableFunctions()\n";
    this->pruneUnreachableFunctions();
    outs() << "[INFO] Running buildPhiFun()\n";
    this->buildPhiFun();
    outs() << "[INFO] Running inferSubGraph()\n";
    this->inferSubGraph();
    // outs() << "[INFO] Running buildR()\n";
    // this->buildR();

    outs() << "[INFO] Dom loading\n";
    ifstream dump_file;
    dump_file.open (file);
    std::string line;
    int l = 0;
    while (std::getline(dump_file, line))
    {
        outs() << "[INFO] Line " << (++l) << "\r";
        std::istringstream iss(line);
        int node_id;
        iss >> node_id;

        IBBNode *node = this->getNode(node_id);

        while (iss >> node_id) {
            // outs() << "node_id " << node->getId() << "\n";
            // outs() << "dom_id " << node_id << "\n";
            // outs() << "before update: " << this->getDom(node).size() << "\n";
            this->addDom(node, this->getNode(node_id));
            // outs() << "after update: " << this->getDom(node).size() << "\n";
        }
    }
    outs() << "\n";
    dump_file.close();
    outs() << "[INFO] Dom loaded correctly\n";

    outs() << "[INFO] Running restoreUnreachableFunctions()\n";
    this->restoreUnreachableFunctions();

    is_created = true;
}

IBBNode *GenericDominatorTy::getNode(int node_id) {

    for (auto node: getRelevantNodes()) {
        if (node->getId() == node_id)
            return node;
    }
    outs() << "[ERROR] Node " << node_id << " not found, abort!\n";
    assert(false);
    // return nullptr;
}

void GenericDominatorTy::buildTransientReduction() {

    // first, I need a map between int and NodeID
    std::map<int, IBBNode*> idNodeMap;

    IBBGraph::IBBNodeSet relevant_nodes = ibbg->getNodeAllocated();

    int V = 0; // number of nodes
    // for (auto n: dom) {
    for (auto node: relevant_nodes) {
        idNodeMap[V] = node;
        V++;
    }

    /* reach[][] will be the output matrix
    // that will finally have the
       shortest distances between
       every pair of vertices */
    int **reach, **tran_red; 
    int i, j, k;
    reach = (int**)malloc(sizeof(int*) * V);
    tran_red = (int**)malloc(sizeof(int*) * V);
    for (i = 0; i < V; i++) {
        reach[i] = (int*)malloc(sizeof(int) * V);
        tran_red[i] = (int*)malloc(sizeof(int) * V);
    }
    IBBNode *node_i, *node_j;

    /* Initialize the solution matrix same
    as input graph matrix. Or
       we can say the initial values of
       shortest distances are based
       on shortest paths considering
       no intermediate vertex. */
    for (i = 0; i < V; i++)
        for (j = 0; j < V; j++) {
            if (i != j) {
                node_i = idNodeMap[i];
                node_j = idNodeMap[j];
                reach[i][j] = dominates(node_i->getFirstNode(), 
                                        node_j->getFirstNode());
            } else {
                reach[i][j] = 0;
            }
        }    

    // Print the shortest distance matrix
    // outs() << "Following matrix is the initial graph\n";
    // for (i = 0; i < V; i++)
    // {
    //     outs() << idNodeMap[i]->getId() << " -> ";
    //     for (int j = 0; j < V; j++)
    //         if (reach[i][j])
    //             outs() << idNodeMap[j]->getId() << " ";
    //             // outs() << reach[i][j] << " ";
    //     // outs() << "\n";
    // }
    // // outs() << "\n";

    // finding longset paths for each node
    for (i = 0; i < V; i++) {
        for (j = 0; j < V; j++) { 
            if (getLongestPath(i, j, reach, V) == 1)
                tran_red[i][j] = 1;
            else 
                tran_red[i][j] = 0;
        }
    }

    DomNode *nodeN1, *nodeN2;

    // Print the shortest distance matrix
    // outs() << "Shortest node for the longest path\n";
    for (i = 0; i < V; i++)
    {
        auto n1 = idNodeMap[i];
        auto n1_id = n1->getId();

        if (hasGNode(n1_id)) {
            nodeN1 = getGNode(n1_id);
        }
        else {
            nodeN1 = new DomNode(n1);
            addGNode(n1_id, nodeN1);
        }

        // outs() << n1_id << " -> ";
        for (int j = 0; j < V; j++)
            if (tran_red[i][j]) {

                auto n2 = idNodeMap[j];
                auto n2_id = n2->getId();

                // outs() << n2_id << " ";
                
                if (hasGNode(n2_id)) {
                    nodeN2 = getGNode(n2_id);
                }
                else {
                    nodeN2 = new DomNode(n2);
                    addGNode(n2_id, nodeN2);
                }

                DomEdge* edge = new DomEdge(nodeN1,nodeN2);
                edge->getDstNode()->addIncomingEdge(edge);
                edge->getSrcNode()->addOutgoingEdge(edge);

            }
        // outs() << "\n";

    }
    // outs() << "\n";
 

    // always clean your dirty room!!
    for (i = 0; i < V; i++) {
        free(reach[i]);
        free(tran_red[i]);
    }
    free(reach);
    free(tran_red);
}

void GenericDominatorTy::topoSort(int u, int *visited, 
                        stack<int>&stack, int **reach, int V) {
    visited[u] = 1;    //set as the node v is visited

    for(int v = 0; v < V; v++) {
        //for allvertices v adjacent to u
        if(reach[u][v]) {
            if(!visited[v])
                topoSort(v, visited, stack, reach, V);
        }
    }

    //push starting vertex into the stack
    stack.push(u);
}

int GenericDominatorTy::getLongestPath(int s, int d, int **reach, int V) {
    if (s < 0 || d < 0 || s >= V || d >= V)
        return -1;

    int *dist = (int*)malloc(sizeof(int) * V);
    memset(dist, 0, sizeof(int) * V);
    
    std::stack<int> stack;
    int *vis = (int*)malloc(sizeof(int) * V);
    memset(vis, 0, sizeof(int) * V);

    for(int i = 0; i< V; i++)
        vis[i] = 0;    // make all nodes as unvisited at first
            
    for(int i = 0; i< V; i++)    //perform topological sort for vertices
        if(!vis[i])
            topoSort(i, vis, stack, reach, V);
                
    for(int i = 0; i< V; i++)
        dist[i] = -1;    //initially all distances are infinity
    dist[s] = 0;    //distance for start vertex is 0
    
    //when stack contains element, process in topological order
    while(!stack.empty()) {
        int nextVert = stack.top(); stack.pop();

        if(dist[nextVert] != -1) {
            for(int v = 0; v < V; v++) {
                if(reach[nextVert][v]) {
                    if(dist[v] < dist[nextVert] + 1)
                        dist[v] = dist[nextVert] + 1;
                }
            }
        }
    }

    int longest_path = dist[d];

    free(dist);
    free(vis);

    return longest_path;
}

// /* DEBUG UTILITIES */
// void GenericDominatorTy::printR() {
//     outs() << "[INFO] Print R\n";
//     for (auto e: R) {
//         outs() << e->toString() << "\n";
//     }
//     outs() << "[INFO] Print R (end)\n";
// }

// void GenericDominatorTy::printC() {
//     outs() << "[INFO] Print C\n";
//     for (auto e: C) {
//         outs() << e->toString() << "\n";
//     }
//     outs() << "[INFO] Print C (end)\n";
// }

void GenericDominatorTy::printPhiFunction() {
    outs() << "[INFO] Print PHI\n";
    for (auto el: phi) {
        outs() << "phi:\n";
        outs() << el.first->toString() << "\n";
        outs() << el.second->toString() << "\n";
        outs() << "\n";
    }
}
void GenericDominatorTy::printPhiInvFunction() {
    outs() << "[INFO] Print PHIInv\n";
    for (auto el: phi_inv) {
        outs() << "phi_inv:\n";
        outs() << el.first->toString() << "\n";
        outs() << el.second->toString() << "\n";
        outs() << "\n";
    }
}
