//===- svf-ex.cpp -- A driver example of SVF-------------------------------------//
//
//                     SVF: Static Value-Flow Analysis
//
// Copyright (C) <2013->  <Yulei Sui>
//

// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.
//
//===-----------------------------------------------------------------------===//

/*
 // A driver program of SVF including usages of SVF APIs
 //
 // Author: Yulei Sui,
 */

#include "Graphs/SVFG.h"
#include "WPA/Andersen.h"
#include "WPA/AndersenPWC.h"
#include "WPA/TypeAnalysis.h"
#include "SVF-LLVM/SVFIRBuilder.h"
#include "Util/Options.h"
#include "Util/SVFUtil.h"
#include "SVF-LLVM/LLVMUtil.h"

#include "GenericDominatorTy.h"
#include "Dominators.h"
#include "PostDominators.h"
#include "AccessType.h"
#include "PhiFunction.h"
#include "IBBG.h"
#include "TypeMatcher.h"
#include "LibfuzzUtil.h"
#include "GlobalStruct.h"

// for random sampling
#include <random>
#include <algorithm>
#include <iterator>

#include "json/json.h"
#include <fstream> 
#include <string>

#include "md5/md5.h"


using namespace std;
using namespace SVF;
using namespace SVFUtil;
using namespace LLVMUtil;

using namespace libfuzz;


// std because stdout gives conflict
enum OutType {txt, json, stdo};

enum Verbosity {v0, v1, v2, v3};

static llvm::cl::opt<std::string> InputFilename(cl::Positional,
        llvm::cl::desc("<input bitcode>"), llvm::cl::init("-"));
static llvm::cl::opt<std::string> FunctionName("function",
        llvm::cl::desc("<function name>"));
static llvm::cl::opt<std::string> LibInterface("interface",
        llvm::cl::desc("<library interface>"));

static llvm::cl::opt<Verbosity> Verbose("v",
        llvm::cl::desc("<verbose>"), llvm::cl::init(v0),
        llvm::cl::values(
            clEnumVal(v0, "No verbose"),
            clEnumVal(v1, "Report ICFG nodes"),
            clEnumVal(v2, "Report Paths if <debug_condition> is met"),
            clEnumVal(v3, "To implement, no effect atm")
        ));

static llvm::cl::opt<std::string> DebugCondition("debug_condition",
        llvm::cl::desc("<debug_condition> in combination with v2"));

static llvm::cl::opt<std::string> ExtractDataLayout("data_layout",
        llvm::cl::desc("<datalayout file>"), llvm::cl::init(""));

static llvm::cl::opt<std::string> OutputFile("output",
        llvm::cl::desc("<output file>"), llvm::cl::init("conditions.json"));
static llvm::cl::opt<OutType> OutputType("t", cl::desc("Output type:"), 
        llvm::cl::init(stdo),
        llvm::cl::values(
            clEnumVal(txt , "Text file <output>"),
            clEnumVal(json, "Json file <output>"),
            clEnumVal(stdo, "Standard output, no <output>")
        ));

static llvm::cl::opt<bool> useDominator("dom",
        llvm::cl::desc("Use Post/Dominators"), llvm::cl::init(false));
static llvm::cl::opt<bool> printDominator("print_dom",
        llvm::cl::desc("Print Post/Dominators"), llvm::cl::init(false));

static llvm::cl::opt<std::string> cacheFolder("cache_folder",
        llvm::cl::desc("Folder for cache"), llvm::cl::init(""));

static llvm::cl::opt<bool> doIndJump("do_indirect_jumps",
        llvm::cl::desc("Include indirect jumps in the analysis"), 
        llvm::cl::init(false));

static llvm::cl::opt<std::string> minimizeApi("minimize_api",
        llvm::cl::desc("Minimize API <out_folder>"), llvm::cl::init(""));

Verbosity verbose;

bool is_fuzzing_compatible(llvm::StructType *st) {

    for (auto el: st->elements())
        if (el->isPointerTy())
            return false;

    return true;
}

// at1 over_dom at2 iif
// for each i2 in at2 . exists i1 in at1 s.t. i1 dom i2
bool dominatesAccessType(GenericDominatorTy *dom, AccessType at1, AccessType at2) {

    uint n_instr_dominated = 0;
    bool is_dominated;
    for (auto i2: at2.getICFGNodes()) {
        is_dominated = false;
        for (auto i1: at1.getICFGNodes()) {
            is_dominated |= dom->dominates( const_cast<ICFGNode*>(i1),
                                            const_cast<ICFGNode*>(i2));
            if (is_dominated)
                break;
        }
        n_instr_dominated += is_dominated ? 1 : 0;
    }

    return n_instr_dominated == at2.getICFGNodes().size();

}

void pruneAccessTypes(Dominator* dom, PostDominator* pDom, 
                        ValueMetadata *meta) {

    // the pair is meant to be <CREATE, DELETE>, not the other way around
    std::set<std::pair<AccessType, AccessType>> pairs_create_delete;
    for (auto at1: *meta->getAccessTypeSet()) {
        if (at1.getAccess() != AccessType::Access::create &&
            at1.getAccess() != AccessType::Access::del)
            continue;

        for (auto at2: *meta->getAccessTypeSet()) {
            if (at2.getAccess() != AccessType::Access::create &&
                at2.getAccess() != AccessType::Access::del)
            continue;

            if (at1 == at2)
                continue;

            if (at1.getFields() == at2.getFields())
                // be sure create comes first
                if (at1.getAccess() == AccessType::Access::create)
                    pairs_create_delete.insert(std::make_pair(at1, at2));

        }
    }

    for (auto px: pairs_create_delete)
        // (delete, X) PostDom (create, X) => None *remove both*
        if (dominatesAccessType(pDom, px.second, px.first)) {
            meta->getAccessTypeSet()->remove(px.first);
            meta->getAccessTypeSet()->remove(px.second);
        // (create, X) Dom (delete, X) => (create, X)
        } else if (dominatesAccessType(dom, px.first, px.second))
            meta->getAccessTypeSet()->remove(px.second);

    // the pair is meant to be <WRITE, READ>, not the other way around
    std::set<std::pair<AccessType, AccessType>> pairs_write_read;
    for (auto at1: *meta->getAccessTypeSet()) {
        if (at1.getAccess() != AccessType::Access::write &&
            at1.getAccess() != AccessType::Access::read)
            continue;

        for (auto at2: *meta->getAccessTypeSet()) {
            if (at2.getAccess() != AccessType::Access::write &&
                at2.getAccess() != AccessType::Access::read)
            continue;

            if (at1 == at2)
                continue;

            if (at1.getFields() == at2.getFields())
                // be sure write comes first
                if (at1.getAccess() == AccessType::Access::write)
                    pairs_write_read.insert(std::make_pair(at1, at2));
        }
    }

    for (auto px: pairs_write_read)
        // (write, X) Dom (read, X) => (write, X) 
        if (dominatesAccessType(dom, px.first, px.second))
            meta->getAccessTypeSet()->remove(px.second);

}

std::string computeHash(std::string file_path) {
    md5::MD5 md5stream;

    std::ifstream a_file;
    a_file.open(file_path);

    //get length of file
    a_file.seekg(0, std::ios::end);
    size_t length = a_file.tellg();
    a_file.seekg(0, std::ios::beg);

    char *buffer = (char*) malloc(length);

    //read file
    a_file.read(buffer, length);
    md5stream.add(buffer, length);

    free(buffer);
    buffer = NULL;
    
    a_file.close();
    return md5stream.getHash();
}

inline bool doesFileExists(const std::string& name) {
    // SVFUtil::outs() << "does it exists?\n";
    // SVFUtil::outs() << name << "\n";
    // exit(1);
    ifstream myfile;
    myfile.open(name);
    if(myfile) {
        myfile.close();
        return true;
    } else {
        return false;
    }
}

std::string getCacheDomFile(std::string fun_name) {
    return cacheFolder + "/" + computeHash(InputFilename) + "_" + fun_name + "_dom.txt";
}

std::string getCachePostDomFile(std::string fun_name) {
    return cacheFolder + "/" + computeHash(InputFilename) + "_" + fun_name + "_postdom.txt";
}

// bool thereIsCache(std::string fun_name) {
//     std::string cache_dom = getCacheDomFile(fun_name);
//     std::string cache_postdom = getCachePostDomFile(fun_name);
//     return exists_file(cache_dom) && exists_file(cache_postdom);
// }

// OLD TEST -- KEPT FOR REFERENCE
void testDom2(FunctionConditions *fun_conds, IBBGraph* ibbg) {

    std::set<const ICFGNode*> cond_nodes;

    int num_param = fun_conds->getParameterNum();

    for (int p = 0; p < num_param; p++) {
        ValueMetadata meta = fun_conds->getParameterMetadata(p);
        for (auto i: meta.getAccessTypeSet()->getAllICFGNodes())
            cond_nodes.insert(i);
    }

    ValueMetadata meta = fun_conds->getReturnMetadata();
    for (auto i: meta.getAccessTypeSet()->getAllICFGNodes())
            cond_nodes.insert(i);

    SVFUtil::outs() << "[DEBUG] All nodes from ATS: " << cond_nodes.size() << "\n";

    std::set<const ICFGNode*> not_found;
    for (auto i: cond_nodes) {
        if (ibbg->getIBBNode(i->getId()) == nullptr)
            not_found.insert(i);
    }

    SVFUtil::outs() << "[DEBUG] Not found " << not_found.size() << "\n";
    // std::set<const SVFFunction*> funs;
    // for (auto i: not_found) {
    //     // SVFUtil::outs() << i->toString() << "\n";
    //     funs.insert(i->getFun());
    // }

    // for (auto f: funs)
    //     SVFUtil::outs() << f->getName() << "\n";
    // exit(1);
}

// OLD TEST -- KEPT FOR REFERENCE
// void testDom(Dominator* dom, IBBGraph* ibbg) {

//     // diff between dom and ibbg nodes

//     // print the diff

//     // find common subset (if any) and check if the 2 doms are coherent

//     SVFUtil::outs() << "[DOING DOM TESTING]\n";

//     // std::set<ICFGNode*> all_nodes = dom->getRelevantNodes();
//     IBBGraph::NodeIDSet all_nodes_id = ibbg->getNodeIdAllocated();
//     std::set<ICFGNode*> all_nodes;
//     for (auto i: all_nodes_id)
//         all_nodes.insert(ibbg->getICFG()->getICFGNode(i));

//     unsigned ok_nodes = 0;

//     srand (time(NULL));

//     unsigned MAX_TEST = 10000;
//     for (int i = 0; i < MAX_TEST; i++) {
//         auto n = rand() % all_nodes.size(); 
//         auto it = std::begin(all_nodes);
//         std::advance(it,n);
//         auto node1 = *it;

//         n = rand() % all_nodes.size(); 
//         it = std::begin(all_nodes);
//         std::advance(it,n);
//         auto node2 = *it;

//         if (SVFUtil::isa<FunEntryICFGNode>(node1) ||
//             SVFUtil::isa<FunEntryICFGNode>(node2))
//             continue;

//         SVFUtil::outs() << "[INFO] TEST " << i << "/" << MAX_TEST << ")\r";

//         bool n1_d_n2_a = dom->dominates(node1, node2);
//         bool n2_d_n1_a = dom->dominates(node2, node1);
//         bool n1_d_n2_b = ibbg->dominates(node1, node2);
//         bool n2_d_n1_b = ibbg->dominates(node2, node1);

//         if (n1_d_n2_a == n1_d_n2_b && n2_d_n1_a == n2_d_n1_b)
//             ok_nodes++;
//         else {
//             SVFUtil::outs() << "\n";
//             SVFUtil::outs() << "Node1: " << node1->toString() << "\n";
//             SVFUtil::outs() << "Node2: " << node2->toString() << "\n";
//             SVFUtil::outs() << "n1_d_n2_a" << n1_d_n2_a << "\n";
//             SVFUtil::outs() << "n2_d_n1_a" << n2_d_n1_a << "\n";
//             SVFUtil::outs() << "n1_d_n2_b" << n1_d_n2_b << "\n";
//             SVFUtil::outs() << "n2_d_n1_b" << n2_d_n1_b << "\n";
//             SVFUtil::outs() << "early stop!\n";
//             exit(1);
        
//         }
//     }

//     SVFUtil::outs() << "\n";
//     SVFUtil::outs() << "OK nodes: " << ok_nodes << "\n";
//     SVFUtil::outs() << "exit for debug\n";
//     exit(1);
// }
DataLayout *DL = nullptr;

void setDataLayout(const Function* F) {
  if (DL == nullptr)
    DL = new DataLayout(F->getParent());
}


int main(int argc, char ** argv)
{

    int arg_num = 0;
    char **arg_value = new char*[argc];
    std::vector<std::string> moduleNameVec;
    LLVMUtil::processArguments(argc, argv, arg_num, arg_value, moduleNameVec);
    cl::ParseCommandLineOptions(arg_num, arg_value,
                                "Extract constraints from functions\n");
    
    bool all_functions = true;
    std::string function;
    if (FunctionName != "") {
        all_functions = false;
        function = FunctionName;
    }

    verbose = Verbose;
    if (verbose >= Verbosity::v2) {
        ValueMetadata::debug = true;
        ValueMetadata::debug_condition = DebugCondition;
    }

    if (Options::WriteAnder() == "ir_annotator")
    {
        LLVMModuleSet::getLLVMModuleSet()->preProcessBCs(moduleNameVec);
    }

    SVFUtil::outs() << "[INFO] Loading library...\n";

    LLVMModuleSet* llvmModuleSet = LLVMModuleSet::getLLVMModuleSet();
    SVFModule* svfModule = LLVMModuleSet::getLLVMModuleSet()->buildSVFModule(moduleNameVec);

    SVFUtil::outs() << "[INFO] Done\n";

    ValueMetadata::consider_indirect_calls = doIndJump;

    // I extract all the function names from the LLVM module
    std::set<std::string> functions_llvm;
    for (const SVFFunction* svfFun : svfModule->getFunctionSet() ){
        auto llvm_val = llvmModuleSet->getLLVMValue(svfFun);
        const llvm::Function* F = SVFUtil::dyn_cast<Function>(llvm_val);
        StringRef function_name = F->getName();
        functions_llvm.insert(function_name.str());
    }

    // std::vector<std::string> functions;
    std::set<std::string> functions;
    // read all the functions from apis_clang.json
    if (all_functions) {
        SVFUtil::outs() << "[INFO] I analyze all the functions\n";

        ifstream f(LibInterface);

        Json::Value root;   
        Json::Reader reader;

        std::string line;
        while (std::getline(f, line)) {
            // SVFUtil::outs() << line << "\n";
            bool parsingSuccessful = reader.parse( line.c_str(), root );
            if ( !parsingSuccessful )
            {
                SVFUtil::outs() << "Failed to parse "
                    << reader.getFormattedErrorMessages();
                exit(1);
            }

            // some clang functions are the result of macro expansion
            // they are not present in the llvm module
            std::string function_name = root["function_name"].asString();
            if (functions_llvm.find(function_name) != functions_llvm.end())
                functions.insert(function_name);
        }

        f.close();
    }
    else {
        SVFUtil::outs() << "[INFO] analyzing function: " << function << "\n";
        // functions.push_back(function);
        functions.insert(function);
    }

    if (OutputType == OutType::stdo)
        SVFUtil::outs() << "[WARNING] outputting in stdout, ignoring OutputFile\n";

    // Dump LLVM apis function per function
    for(const SVFFunction* svfFun : svfModule->getFunctionSet() ){
        auto llvm_val = llvmModuleSet->getLLVMValue(svfFun);
        const llvm::Function* F = SVFUtil::dyn_cast<Function>(llvm_val);

        setDataLayout(F);
        libfuzz::function_record my_fun;

        Type * retType = F->getReturnType();
        StringRef function_name = F->getName();
        bool is_vararg = F->isVarArg();
    
        SVFUtil::errs() << "Doing: " << function_name.str() << "\n";

        my_fun.function_name = function_name.str();
        my_fun.is_vararg = is_vararg ? "true" : "false";
        my_fun.return_info.set_from_type(retType);
        my_fun.return_info.size = libfuzz::estimate_size(retType, false, DL);
        my_fun.return_info.name = "return";

        for(const auto& arg : F->args()) {
            libfuzz::argument_record an_argument;
            an_argument.set_from_argument(arg);
            an_argument.size = libfuzz::estimate_size(arg.getType(), arg.hasByValAttr(), DL);
            my_fun.arguments_info.push_back(an_argument);
        }
      
      libfuzz::dumpApiInfo(my_fun);
    }
    /// Build Program Assignment Graph (SVFIR)
    SVFIRBuilder builder(svfModule);
    SVFIR* pag = builder.build();
    ICFG* icfg = pag->getICFG();
    /// Create Andersen's pointer analysis
    // Andersen* point_to_analysys = AndersenWaveDiff::createAndersenWaveDiff(pag);
    // FlowSensitive* point_to_analysys = FlowSensitive::createFSWPA(pag);
    // AndersenSCD* point_to_analysys = AndersenSCD::createAndersenSCD(pag);
    // TypeAnalysis* point_to_analysys = new TypeAnalysis(pag);
    GlobalStruct *point_to_analysys = GlobalStruct::createSGWPA(pag);

    point_to_analysys->analyze();

    SVFUtil::outs() << "[INFO] Analysis done!\n";

    GlobalStruct::CallEdgeMap newEdges = point_to_analysys->get_new_edges();
    // NOTE: copy callsite->target relation in a neutral structure
    for (auto x: newEdges) {
        auto cs = x.first;
        for (auto t: x.second)
            ValueMetadata::myCallEdgeMap_inst[cs].insert(t);
    }

    Dominator *dom = nullptr;
    PostDominator *pDom = nullptr;

    PAG::FunToArgsListMap funmap_par = pag->getFunArgsMap();

    // for (auto x: funmap_par) {
    //     SVFUtil::outs() << x.first << "\n";
    //     SVFUtil::outs() << x.second.size() << "\n";
    // }
    // exit(1);

    PAG::FunToRetMap funmap_ret = pag->getFunRets();

    PTACallGraph* callgraph = point_to_analysys->getPTACallGraph();
    builder.updateCallGraph(callgraph);
    icfg = pag->getICFG();
    icfg->updateCallGraph(callgraph);


    // icfg->dump("icfg_extractor");

    /// Sparse value-flow graph (SVFG)
    SVFGBuilder svfBuilder;
    SVFG* svfg = svfBuilder.buildFullSVFG(point_to_analysys);
    svfg->updateCallGraph(point_to_analysys);

    // svfg->dump("from_extractor");

    // I want to find a minimized set of APIs to analyze
    if (minimizeApi != "") {

        std::set<std::string> minimize_functions;

        SVF::SVFModule::const_iterator it = svfModule->begin();
        SVF::SVFModule::const_iterator eit = svfModule->end();
        for (;it != eit; ++it) {
            const SVFFunction *fun = *it;
            std::string fun_name = fun->getName();
            if (functions.find(fun_name) != functions.end()) {
                auto cg_node = callgraph->getCallGraphNode(fun);

                bool no_direct_in_edge = true;

                auto it2 = cg_node->directInEdgeBegin();
                auto eit2 = cg_node->directInEdgeEnd();
                for (; it2 != eit2; it2++){
                    no_direct_in_edge = false;
                    break;
                }
                
                if (no_direct_in_edge)
                    minimize_functions.insert(fun_name);
            }
        }

        // SVFUtil::outs() << "[INFO] The minimize set of function\n";
        std::ofstream minimizeApiFile(minimizeApi);
        for (auto f: minimize_functions) {
            minimizeApiFile << f << "\n";
        }
        minimizeApiFile.close();
        // SVFUtil::outs() << "[INFO] All function\n";
        // for (auto f: functions)
        //     SVFUtil::outs() << f << "\n";
    
        // SVFUtil::outs() << "[INFO] Total: " << minimize_functions.size() << "\n";
        // SVFUtil::outs() << "[INFO] Original: " << functions.size() << "\n";

    }

    // SVFUtil::outs() << " === EXIT FOR DEBUG ===\n";
    // exit(1);

    FunctionConditionsSet fun_cond_set;

    unsigned int tot_function = functions.size();
    unsigned int num_function = 0;

    SVFUtil::outs() << "[INFO] running analysis...\n";
    for (auto f: functions) {

        num_function++;
        FunctionConditions fun_conds;
        std::string prog = std::to_string(num_function) + "/" + 
                            std::to_string(tot_function);

        fun_conds.setFunctionName(f);
        for (auto const& x : funmap_par) {
            const SVFFunction *fun = x.first;
            if ( fun->getName() != f)
                continue;

            SVFUtil::outs() << "[INFO " << prog << "] processing params for: " 
                << fun->getName() << "\n";
                        
            for (auto const& p : x.second) {
                if (verbose >= Verbosity::v1)
                    SVFUtil::outs() << "[INFO] param: " << p->toString() << "\n";

                auto val = p->getValue();
                auto llvm_val = llvmModuleSet->getLLVMValue(val);
                auto seek_type = llvm_val->getType();
                ValueMetadata paramMetadata = 
                    ValueMetadata::extractParameterMetadata(
                        svfg, llvm_val, seek_type);

                // auto param_key = "param_" + std::to_string(pn);
                // functionResult[param_key] = paramMetadata.toJson();

                if (paramMetadata.isArray()) {
                    auto depends_on = 
                        ValueMetadata::extractLenDependencyParameter(
                        p, &paramMetadata, svfg, fun);

                    if (depends_on != "")
                        paramMetadata.setLenDependency(depends_on);
                }

                // find "generic" dependencies between parameters
                auto set_by_vect = 
                    ValueMetadata::extractDependencyAmongParameters(
                            p, &paramMetadata, svfg, fun);

                for (auto d: set_by_vect)
                    paramMetadata.addSetByDependency(d);
            
                fun_conds.addParameterMetadata(paramMetadata);
            }
        }

        for (auto const& x : funmap_ret) {
            const SVFFunction *fun = x.first;
            if ( fun->getName() != f)
                continue;

            SVFUtil::outs() << "[INFO " << prog << "] processing return for: " 
                << fun->getName() << "\n";

            auto p = x.second;
            if (verbose >= Verbosity::v1)
                SVFUtil::outs() << "[INFO] return: " << p->toString() << "\n";
            auto llvm_value = llvmModuleSet->getLLVMValue(p->getValue());
            ValueMetadata returnMetadata =
                ValueMetadata::extractReturnMetadata(svfg, llvm_value);

            // functionResult["return"] = returnAccessTypeSet.toJson();
            // jsonResult.append(functionResult);
            fun_conds.setReturnMetadata(returnMetadata);
        }

        if (useDominator) {
            SVF::SVFModule::const_iterator it = svfModule->begin();
            SVF::SVFModule::const_iterator eit = svfModule->end();
            for (;it != eit; ++it) {
                const SVFFunction *fun = *it;
                if ( fun->getName() != f)
                    continue;

                std::string fun_name = fun->getName();

                SVFUtil::outs()  << "[INFO] computing dominators for: " <<
                            fun_name << "\n";

                FunEntryICFGNode *fun_entry = icfg->getFunEntryICFGNode(fun);
                FunExitICFGNode *fun_exit = icfg->getFunExitICFGNode(fun);

                std::string dom_cache_file = getCacheDomFile(fun_name);
                std::string postdom_cache_file = getCachePostDomFile(fun_name);

                dom = new Dominator(point_to_analysys, fun_entry, doIndJump);
                // SVFUtil::outs() << "[INFO] Running pruneUnreachableFunctions()\n";
                // dom->pruneUnreachableFunctions();
                // SVFUtil::outs() << "[INFO] Running buildPhiFun()\n";
                // dom->buildPhiFun();
                // SVFUtil::outs() << "[INFO] Running inferSubGraph()\n";
                // dom->inferSubGraph();
                if (cacheFolder != "" && doesFileExists(dom_cache_file)) {
                    SVFUtil::outs() << "[INFO] There is DOM cache, loading it\n";
                    dom->loadDom(dom_cache_file);
                } else {
                    SVFUtil::outs() << "[INFO] No DOM cache, computing from scratch and save\n";
                    auto begin = chrono::high_resolution_clock::now();    
                    dom->createDom();
                    auto end = chrono::high_resolution_clock::now();    
                    auto dur = end - begin;
                    auto min = std::chrono::duration_cast<std::chrono::minutes>(dur).count();
                    SVFUtil::outs() << "[TIME] Dom: " << min << "min\n";
                    // dom->saveIBBGraph("ibbgraph_2");
                    
                    if (cacheFolder != "")
                        dom->dumpDom(dom_cache_file);
                }

                pDom = new PostDominator(point_to_analysys, fun_entry, 
                                        fun_exit, doIndJump);
                if (cacheFolder != "" && doesFileExists(postdom_cache_file)) {
                    SVFUtil::outs() << "[INFO] There is POSTDOM cache, loading it\n";
                    pDom->loadDom(postdom_cache_file);
                } else {
                    SVFUtil::outs() << "[INFO] No POSTDOM cache, computing from scratch and save\n";
                    auto begin = chrono::high_resolution_clock::now();    
                    pDom->createDom();
                    auto end = chrono::high_resolution_clock::now();    
                    auto dur = end - begin;
                    auto min = std::chrono::duration_cast<std::chrono::minutes>(dur).count();
                    SVFUtil::outs() << "[TIME] Postdom: " << min << "min\n";
                    // pDom->saveIBBGraph("ibbgraph_3");

                    if (cacheFolder != "")
                        pDom->dumpDom(postdom_cache_file);
                }

                if (printDominator) {
                    SVFUtil::outs() << "[INFO] dumping dominators...\n";
                    std::string str1, str2;
                    if (dom) {
                        dom->dumpTransRed("./" + dom_cache_file);
                    }

                    if (pDom) {
                        pDom->dumpTransRed("./" + postdom_cache_file);
                    }
                }

                // FOR TESTING DOM CORRECTNESS
                testDom2(&fun_conds, dom->getIBBGraph());
                // testDom(dom, ibb_graph);

                int num_param = fun_conds.getParameterNum();

                for (int p = 0; p < num_param; p++) {
                    ValueMetadata meta = fun_conds.getParameterMetadata(p);
                    pruneAccessTypes(dom, pDom, &meta);
                    fun_conds.replaceParameterMetadata(p, meta);
                }

                ValueMetadata meta = fun_conds.getReturnMetadata();
                pruneAccessTypes(dom, pDom, &meta);
                fun_conds.setReturnMetadata(meta);

                delete dom;
                dom = nullptr;
                delete pDom;
                pDom = nullptr;
            }
        }

        fun_cond_set.addFunctionConditions(fun_conds);

    }

    if (OutputType == OutType::txt) {
        FunctionConditionsSet::storeIntoTextFile(
            fun_cond_set, OutputFile, verbose >= Verbosity::v1);
    } else if (OutputType == OutType::json) {
        FunctionConditionsSet::storeIntoJsonFile(
            fun_cond_set, OutputFile, verbose >= Verbosity::v1);
    } else if (OutputType == OutType::stdo) {
        SVFUtil::outs() << fun_cond_set.toString(verbose >= Verbosity::v1);
    }

    SVFUtil::outs() << fun_cond_set.getSummary();

    // extract data layout
    if (ExtractDataLayout != "") {
        SVFUtil::outs() << "\n[INFO] extract structs data layout!\n";

        Module *m = LLVMModuleSet::getLLVMModuleSet()->getMainLLVMModule();
        const DataLayout &data_layout = m->getDataLayout();

        ofstream fw(ExtractDataLayout, std::ofstream::out);
        if (fw.is_open())
        {
            for (auto st: m->getIdentifiedStructTypes()) {
                fw << st->getName().str() << " ";
                if (st->isSized()) {
                    uint64_t storeSize = data_layout.getTypeStoreSizeInBits(st);
                    fw << storeSize << " ";
                    fw << TypeMatcher::compute_hash(st) << " ";
                    fw << is_fuzzing_compatible(st) << "\n";
                } else {
                    fw << "0 <random> 0\n";
                }
            }
            fw.close();
        }        

        SVFUtil::outs() << "[INFO] struct data layout done!\n";
    }

    // clean up memory
    if (dom)
        delete dom;

    if (pDom)
        delete pDom;

    AndersenWaveDiff::releaseAndersenWaveDiff();
    SVFIR::releaseSVFIR();

    // I am not sure I need this
    // LLVMModuleSet::getLLVMModuleSet()->dumpModulesToFile(".svf.bc");
    SVF::LLVMModuleSet::releaseLLVMModuleSet();

    llvm::llvm_shutdown();
    return 0;
}
