
#include "TypeMatcher.h"

TypeMatcher::TypeStringMap TypeMatcher::type_hash_map;
TypeMatcher::TypeStringMap TypeMatcher::type_id_map;

std::string TypeMatcher::compute_id(const llvm::StructType* t) {

    if (type_id_map.find(t) != type_id_map.end())
        return type_id_map[t];

    std::string name;
    if (t->hasName()) {
        name = remove_trail_num(t->getName().str());
    } else {
        name = "none";
    }

    type_id_map[t] = name;

    return name;
}

std::string TypeMatcher::compute_unique_string(const llvm::Type* t,
    std::set<std::string> ids_done) {

    if (type_hash_map.find(t) != type_hash_map.end())
        return type_hash_map[t];

    std::string hash = "";

    switch(t->getTypeID()) {
        case llvm::Type::TypeID::HalfTyID:
            hash += "HA";
            break;
        case llvm::Type::TypeID::BFloatTyID:
            hash += "BF";
            break;
        case llvm::Type::TypeID::FloatTyID:
            hash += "FL";
            break;
        case llvm::Type::TypeID::DoubleTyID:
            hash += "DO";
            break;
        case llvm::Type::TypeID::X86_FP80TyID:
            hash += "F8";
            break;
        case llvm::Type::TypeID::FP128TyID:
            hash += "FP";
            break;
        case llvm::Type::TypeID::PPC_FP128TyID:
            hash += "PP";
            break;
        case llvm::Type::TypeID::VoidTyID:
            hash += "VO";
            break;
        case llvm::Type::TypeID::LabelTyID:
            hash += "LA";
            break;
        case llvm::Type::TypeID::MetadataTyID:
            hash += "ME";
            break;
        case llvm::Type::TypeID::X86_MMXTyID:
            hash += "MX";
            break;
        case llvm::Type::TypeID::X86_AMXTyID:
            hash += "AM";
            break;
        case llvm::Type::TypeID::TokenTyID:
            hash += "TO";
            break;
        case llvm::Type::TypeID::IntegerTyID:
            hash += "IN";
            break;
        case llvm::Type::TypeID::FunctionTyID:
            {
            hash += "FN["; // compute hash function

            const llvm::FunctionType* ft = SVFUtil::dyn_cast<FunctionType>(t);

            // std::string t_id = compute_id(st);

            auto ret_type = ft->getReturnType();
            unsigned int n_arg = ft->getNumParams();
            hash += std::to_string(n_arg+1) + ",";
          
            hash += compute_unique_string(ret_type, ids_done) + ",";
            unsigned int i = 0;
            for (; i < n_arg; i++) {
                auto at = ft->getParamType(i);
                hash += compute_unique_string(at, ids_done) + ",";
            }

                
            hash = hash.substr(0, hash.size()-1); // remove last ","
            hash += "]";
            }
            break;
        case llvm::Type::TypeID::PointerTyID: 
            {
            const llvm::PointerType* pt = SVFUtil::dyn_cast<PointerType>(t);
            hash += "PN[" + compute_unique_string(pt->getElementType(), ids_done) + "]";
            }
            break;
        case llvm::Type::TypeID::StructTyID:
            {
            const llvm::StructType* st = SVFUtil::dyn_cast<StructType>(t);

            std::string t_id = compute_id(st);

            if (st->isEmptyTy()) {
                hash += "FN";
            } else {
                hash += "ST[" + t_id + "]";
                // hash += "ST[" + t_id + "," + 
                //         std::to_string(st->getNumElements()) + ",";

                // bool to_expand = ids_done.find(t_id) == ids_done.end();
                // ids_done.insert(t_id);
                // for (auto el: st->elements())
                //     if (to_expand)
                //         hash += compute_unique_string(el, ids_done) + ",";
                //     else
                //         hash += "x,";
                
                // hash = hash.substr(0, hash.size()-1); // remove last ","
                // hash += "]";
            }
            }
            break;
        case llvm::Type::TypeID::ArrayTyID:
            {
            const llvm::ArrayType* ar = SVFUtil::dyn_cast<ArrayType>(t);
            hash += "AR[" + std::to_string(ar->getNumElements());
            hash += "," + compute_unique_string(ar->getElementType(), ids_done);
            hash += "]";
            }
            break;
        case llvm::Type::TypeID::FixedVectorTyID:
            {
            const llvm::FixedVectorType* fv = SVFUtil::dyn_cast<FixedVectorType>(t);
            hash += "FV[" + std::to_string(fv->getNumElements());
            hash += "," + compute_unique_string(fv->getElementType(), ids_done);
            hash += "]";
            }
            break;
        case llvm::Type::TypeID::ScalableVectorTyID:
            {
            const llvm::ScalableVectorType* fv = 
                SVFUtil::dyn_cast<ScalableVectorType>(t);
            hash += "SV[" + std::to_string(fv->getMinNumElements());
            hash += "," + compute_unique_string(fv->getElementType(), ids_done);
            hash += "]";
            }
            break;
        default:
            outs() << "[ERROR] Invalid Type!\n";
            exit(1);

    }

    type_hash_map[t] =  hash;

    return hash;
}

std::string TypeMatcher::compute_hash(const llvm::Type* t) {

    std::string hash = TypeMatcher::compute_unique_string(t);

    md5::MD5 md5stream;
    md5stream.add(hash.c_str(), hash.length());
    hash = md5stream.getHash();

    return hash;
}

bool TypeMatcher::compare_types(const llvm::Type* t1, const llvm::Type* t2) {
    return compute_hash(t1) == compute_hash(t2);
}


std::string TypeMatcher::remove_trail_num(std::string n) {

    // std::string to_ret = "";

    char trail_chrs[] = {'1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '.'};

    int i = n.size() - 1;

    bool has_bad_char = true;
    while (has_bad_char) {
        has_bad_char = false;
        for (int c = 0; c < sizeof(trail_chrs); c++)
            if (n[i] == trail_chrs[c]) {
                has_bad_char = true;
                break;
            }
        i--;
        if (i < 0)
            break;
    }

    return std::string(&n[0], &n[i+2]);
}
