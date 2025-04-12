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

#include "PhiFunction.h"
#include "TypeMatcher.h"
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

static llvm::cl::opt<std::string> OutputFile("output",
        llvm::cl::desc("<output file>"), llvm::cl::init("conditions.json"));
static llvm::cl::opt<OutType> OutputType("t", cl::desc("Output type:"), 
        llvm::cl::init(stdo),
        llvm::cl::values(
            clEnumVal(txt , "Text file <output>"),
            clEnumVal(json, "Json file <output>"),
            clEnumVal(stdo, "Standard output, no <output>")
        ));

static llvm::cl::opt<bool> doIndJump("do_indirect_jumps",
        llvm::cl::desc("Include indirect jumps in the analysis"), 
        llvm::cl::init(false));

Verbosity verbose;

DataLayout *DL = nullptr;

void setDataLayout(const Function* F) {
  if (DL == nullptr)
    DL = new DataLayout(F->getParent());
}

void dumpToText(std::map<std::string, unsigned int> *weights) {

    ofstream ofile;
    ofile.open(OutputFile);
    
    for (auto el: *weights) {
        auto fun_name = el.first;
        auto weight = el.second;
        ofile << fun_name << " " << weight << "\n";
    }  

    ofile.close();

}

void dumpToStdout(std::map<std::string, unsigned int> *weights) {
    for (auto el: *weights) {
        auto fun_name = el.first;
        auto weight = el.second;
        SVFUtil::outs() << fun_name << " " << weight << "\n";
    }  

}

void dumpToJson(std::map<std::string, unsigned int> *weights) {
    // Json::Value jsonResult = fun_cond_set.toJson(verbose);

    Json::Value jsonResult(Json::objectValue);

   for (auto el: *weights) {
        auto fun_name = el.first;
        auto weight = el.second;
        
        jsonResult[fun_name] = weight;
   }

    std::ofstream jsonOutFile(OutputFile);
    Json::StreamWriterBuilder jsonBuilder;
    if (!verbose)
        jsonBuilder.settings_["indentation"] = "";
        
    std::unique_ptr<Json::StreamWriter> writer(
        jsonBuilder.newStreamWriter());

    writer->write(jsonResult, &jsonOutFile);
    jsonOutFile.close();
}

unsigned int countReachableInst(SVFIR* pag, ICFG* icfg, 
    const SVFFunction* svfFun) {

    SVFModule *svfModule = pag->getModule();

    PHIFun phi;
    PHIFunInv phi_inv;
    getPhiFunction(svfModule, icfg, &phi, &phi_inv);  

    std::set<const Instruction*> allocainst_set;

    std::set<const SVFFunction*> visited_functions;

    FunEntryICFGNode *entry_node = icfg->getFunEntryICFGNode(svfFun);

    std::stack<std::pair<ICFGNode*,std::stack<ICFGEdge*>>> working;

    std::set<ICFGNode*> visited;

    std::stack<ICFGEdge*> empty_stack;
    working.push(std::make_pair(entry_node, empty_stack));

    while(!working.empty()) {

        auto el = working.top();
        working.pop();

        ICFGNode *node = el.first;
        std::stack<ICFGEdge*> curr_stack = el.second;

        // We'll go throught the children and add unknown ones to our work list.
        // outs() << "NODE: " << node->toString() << "\n";
        if (node->hasOutgoingEdge()) {
            ICFGNode::const_iterator it = node->OutEdgeBegin();
            ICFGNode::const_iterator eit = node->OutEdgeEnd();
        
            for (; it != eit; ++it) {
                ICFGEdge *edge = *it;
                ICFGNode *dst = edge->getDstNode();

                if (visited.find(dst) != visited.end()) {
                    // We've seen it already

                    // BUG: if CallCFGEdge and already visited, then skip the
                    // call and go to the next return                
                    if(auto call_edge = SVFUtil::dyn_cast<CallCFGEdge>(edge)) {
                        ICFGEdge *next_ret = phi[call_edge];
                        ICFGNode *dst_new = next_ret->getDstNode();
                        // next_ret
                        // curr_stack.push(next_ret);
                        working.push(std::make_pair(dst_new, curr_stack));
                    }

                    // outs() << "\talready visited: ";
                    // outs() << dst->toString() << "\n";
                    continue;
                }
                
                if(auto ret_edge = SVFUtil::dyn_cast<RetCFGEdge>(edge)) {

                    if (curr_stack.size() != 0) {
                        ICFGEdge *ret = curr_stack.top();
                        if (ret_edge == ret) {
                            curr_stack.pop();
                            working.push(std::make_pair(dst, curr_stack));
                            visited.insert(dst);
                        }
                    }
                }
                else if(auto call_edge = SVFUtil::dyn_cast<CallCFGEdge>(edge)) {
                    ICFGEdge *next_ret = phi[call_edge];
                    curr_stack.push(next_ret);
                    working.push(std::make_pair(dst, curr_stack));
                    visited.insert(dst);
                }
                 else {
                    working.push(std::make_pair(dst, curr_stack));
                    visited.insert(dst);
                }
            }
        }

    }
    // We have visited all the nodes
    return visited.size();
}

/*
example of usage:
./bin/extractor /workspaces/libfuzz/analysis/libaom/work/lib/libaom.a.bc \
    -interface /workspaces/libfuzz/analysis/libaom/work/apipass/apis_clang.json \
    -do_indirect_jumps -v v0 -t json -output weights.json
*/
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
    
    if (Options::WriteAnder() == "ir_annotator")
    {
        LLVMModuleSet::getLLVMModuleSet()->preProcessBCs(moduleNameVec);
    }

    SVFUtil::outs() << "[INFO] Loading library...\n";

    LLVMModuleSet* llvmModuleSet = LLVMModuleSet::getLLVMModuleSet();
    SVFModule* svfModule = LLVMModuleSet::getLLVMModuleSet()->buildSVFModule(moduleNameVec);

    SVFUtil::outs() << "[INFO] Done\n";

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

    // /// Sparse value-flow graph (SVFG)
    // SVFGBuilder svfBuilder;
    // SVFG* svfg = svfBuilder.buildFullSVFG(point_to_analysys);
    // svfg->updateCallGraph(point_to_analysys);

    // svfg->dump("from_extractor");

    // SVFUtil::outs() << " === EXIT FOR DEBUG ===\n";
    // exit(1);

    unsigned int tot_function = functions.size();
    unsigned int num_function = 0;

    std::map<std::string, unsigned int> weights;

    SVFUtil::outs() << "[INFO] running analysis...\n";
    for(const SVFFunction* svfFun : svfModule->getFunctionSet() ){
        auto llvm_val = llvmModuleSet->getLLVMValue(svfFun);
        const llvm::Function* F = SVFUtil::dyn_cast<Function>(llvm_val);

        std::string function_name = F->getName().str();

        if (functions.find(function_name) == functions.end())
            continue;

        num_function++;
        std::string prog = std::to_string(num_function) + "/" + 
                            std::to_string(tot_function);

        // SVFUtil::outs() << "Processing " << f << "\n";
        SVFUtil::outs() << "[INFO " << prog << "] processing: " 
                << function_name << "\n";

        unsigned int n_instruction = countReachableInst(pag, icfg, svfFun); 
        SVFUtil::outs() << "[INFO] N. Inst.: " << n_instruction << "\n";
        weights[function_name] = n_instruction;
    }


    if (OutputType == OutType::txt) {
        dumpToText(&weights);
    } else if (OutputType == OutType::json) {
        dumpToJson(&weights);
    } else if (OutputType == OutType::stdo) {
        dumpToStdout(&weights);
    }

    AndersenWaveDiff::releaseAndersenWaveDiff();
    SVFIR::releaseSVFIR();

    // I am not sure I need this
    // LLVMModuleSet::getLLVMModuleSet()->dumpModulesToFile(".svf.bc");
    SVF::LLVMModuleSet::releaseLLVMModuleSet();

    llvm::llvm_shutdown();
    return 0;
}
