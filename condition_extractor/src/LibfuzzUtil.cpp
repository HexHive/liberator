//===- HexTypeUtil.cpp - helper functions and classes for HexType ---------===//
////
////                     The LLVM Compiler Infrastructure
////
//// This file is distributed under the University of Illinois Open Source
//// License. See LICENSE.TXT for details.
////
////===--------------------------------------------------------------------===//

#include "llvm/Pass.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/Module.h"
#include "llvm/Support/CommandLine.h"
#include "llvm/IR/LegacyPassManager.h"
#include "llvm/IR/Constants.h"
#include "llvm/IR/InstVisitor.h"
#include "llvm/IR/IntrinsicInst.h"
#include "llvm/IR/Argument.h"
#include "llvm/Transforms/IPO/PassManagerBuilder.h"
#include "LibfuzzUtil.h"
#include "llvm/Transforms/Utils/BasicBlockUtils.h"

#include <sys/types.h>
#include <unistd.h>
#include <inttypes.h>
#include <filesystem>
#include <string>
#include <iostream>
#include <fstream>
#include <ios>

#define MAXLEN 1000

using namespace llvm;

namespace libfuzz {
  // cl::opt<bool> ClCreateCastRelatedTypeList(
  // "create-cast-related-type-list",
  // cl::desc("create casting related object list"),
  // cl::Hidden, llvm::cl::init(false));

  std::string CoerceFilePath = "";
  std::string ApiFilePath = "";

  std::string getCoerceFileLog() {
    if (CoerceFilePath == "") {
      if(getenv("LIBFUZZ_LOG_PATH")) {
        char buff[1000];
        strcpy(buff, getenv("LIBFUZZ_LOG_PATH"));
        CoerceFilePath = std::string(buff) + "/coerce.log";
      } else {
        errs() << "LIBFUZZ_LOG_PATH not found, set it!\n";
        exit(1);
      }
    }
    return CoerceFilePath;
  }

  std::string getApiFileLog() {
    if (ApiFilePath == "") {
      if(getenv("LIBFUZZ_LOG_PATH")) {
        char buff[1000];
        strcpy(buff, getenv("LIBFUZZ_LOG_PATH"));
        ApiFilePath = std::string(buff) + "/apis_llvm.json";
      } else {
        errs() << "LIBFUZZ_LOG_PATH not found, set it!\n";
        exit(1);
      }
    }
    return ApiFilePath;
  }

  void dumpLine(std::string line, std::string fileName) {
    std::ofstream log(fileName, std::ios_base::app | std::ios_base::out);
    log << line;
    log.close();
  }

  void dumpCoerceMap(llvm::Function *func, unsigned arg_pos, std::string arg_original_name, std::string arg_original_type,  llvm::Argument *arg_coerce) {
    std::string fileName = getCoerceFileLog();

    llvm::DataLayout* DL = new DataLayout(func->getParent());

    llvm::Type *arg_coerce_type = arg_coerce->getType();

    std::string arg_coerce_name = arg_coerce->getName().str();
    uint64_t arg_coerce_size = estimate_size(arg_coerce_type, arg_coerce->hasByValAttr(), DL);
    std::string arg_coerce_type_str;
    llvm::raw_string_ostream ostream(arg_coerce_type_str);
    arg_coerce_type->print(ostream);
    std::string line = func->getName().str() + "|" + std::to_string(arg_pos) + "|" + arg_original_name + "|" + arg_original_type + "|" + arg_coerce_name + "|" + arg_coerce_type_str + "|" + std::to_string(arg_coerce_size) + "\n";
    dumpLine(line, fileName);
  }

  void dumpApiInfo(function_record a_fun) {
    std::string fileName = getApiFileLog();
    std::string line = a_fun.to_json() + "\n";
    dumpLine(line, fileName);
  }

  uint64_t estimate_size(llvm::Type* a_type, bool has_byval, llvm::DataLayout* DL) {
    
    Type *typ_pointed = a_type;

    if (has_byval && isa<PointerType>(a_type) ) {
      PointerType *a_ptrtype = dyn_cast<PointerType>(a_type);
      typ_pointed = a_ptrtype->getElementType();
    }

    return typ_pointed->isSized() ? DL->getTypeSizeInBits(typ_pointed) : 0;
  }

}
