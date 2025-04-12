#ifndef INCLUDE_DOM_TYPEMATCHER_H_
#define INCLUDE_DOM_TYPEMATCHER_H_

#include "SVF-LLVM/LLVMUtil.h"
#include "md5/md5.h"

#include <string>

using namespace SVF;
using namespace llvm;
using namespace std;

class TypeMatcher {
    public:
        typedef std::map<const Type*, std::string> TypeStringMap;

        static TypeStringMap type_hash_map;
        static TypeStringMap type_id_map;

        static std::string compute_id(const llvm::StructType*);
        static std::string compute_hash(const llvm::Type* t);
        static std::string compute_unique_string(const llvm::Type* t, 
            std::set<std::string> ids_done = {});
        static bool compare_types(const llvm::Type*, const llvm::Type*);
        static std::string remove_trail_num(std::string);
};

#endif
