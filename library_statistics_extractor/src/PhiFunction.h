
#ifndef INCLUDE_PHI_FUNCTION_H_
#define INCLUDE_PHI_FUNCTION_H_

#include "SVF-LLVM/LLVMUtil.h"
#include "Graphs/ICFG.h"
#include "Graphs/SVFG.h"
#include <Graphs/GenericGraph.h>
#include "WPA/Andersen.h"

using namespace SVF;
using namespace llvm;
using namespace std;

typedef std::map<CallCFGEdge*, RetCFGEdge*> PHIFun;
typedef std::map<RetCFGEdge*, CallCFGEdge*> PHIFunInv;

void getPhiFunction(SVFModule*, ICFG*, PHIFun*, PHIFunInv*);

#endif
