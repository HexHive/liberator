#ifndef INCLUDE_DOM_ACCESSTYPE_H_
#define INCLUDE_DOM_ACCESSTYPE_H_

#include "Graphs/ICFG.h"
#include "Graphs/SVFG.h"
#include <Graphs/GenericGraph.h>
#include "WPA/Andersen.h"
#include <llvm/Support/raw_ostream.h>
#include <llvm/Analysis/LoopInfo.h>
#include <llvm/IR/Dominators.h>

#include "PhiFunction.h"
#include "TypeMatcher.h"
#include "json/json.h"
#include <fstream> 
#include <utility>

using namespace SVF;
using namespace llvm;
using namespace std;

class AccessType {
    public:
        typedef enum _access { read, write, ret, 
                                del, create, none, 
                                file, input_stream, output_stream } Access;


    private:
        std::set<const ICFGNode*> icfg_set;
        std::vector<int> fields;
        Access access;
        const llvm::Type* type;

        // fake parent
        bool has_parent;
        std::vector<int> p_fields;
        Access p_access;
        const llvm::Type* p_type;

        // original casted type
        const llvm::Type* c_type;
        
        // remember the types extracted from previous GEP
        std::set<const llvm::Type*> visited_types;

        static std::string type_to_string(const llvm::Type* typ) {
            std::string str;
            llvm::raw_string_ostream(str) << *typ;
            return str;
        }

        static std::string type_to_hash(const llvm::Type* typ) {
            return TypeMatcher::compute_hash(typ);
        }

    public:
        AccessType(const llvm::Type* t) {
            access = none;
            p_access = none;
            has_parent = false;
            type = t;
            p_type = nullptr;
            c_type = nullptr;
        }
        ~AccessType() {fields.clear();}

        void add_visited_type(llvm::Type* a_type) {
            visited_types.insert(a_type);
        }

        bool is_visited(llvm::Type* a_type) {
            return visited_types.find(a_type) != visited_types.end();
        }

        // copy assignment operator
        AccessType& operator=(const AccessType &rhs) {
            this->fields = rhs.fields;
            this->access = rhs.access;
            this->type = rhs.type;

            // hope this does not make a mess!
            this->icfg_set = rhs.icfg_set;

            // parent
            this->has_parent = rhs.has_parent;
            this->p_fields = rhs.p_fields;
            this->p_access = rhs.p_access;
            this->p_type = rhs.p_type;

            // visited types for GEP recursion
            this->visited_types = rhs.visited_types;

            return *this;
        };

        void addICFGNode(const ICFGNode* icfg_node) {
            icfg_set.insert(icfg_node);
        }

        std::set<const ICFGNode*> getICFGNodes() const {
            return icfg_set;
        }

        const llvm::Type* getOriginalCastType() {
            return c_type;
        }

        void setOriginalCastType(const llvm::Type* t) {
            c_type = t;
        }

        void addField(int a_field) {
            // fake father? find better way to do so
            p_fields = fields;
            p_access = access;
            p_type = type;
            has_parent = true;
            fields.push_back(a_field);
        }

        std::vector<int> getFields() {
            return fields;
        }

        int getNumFields() {
            return fields.size();
        }

        void removeLastField() {
            if (getNumFields() == 0)
                return;
            fields.pop_back();
        }

        int getLastField() {
            if (getNumFields() == 0)
                return -1;
            return fields.back();
        }

        void setAccess(Access a_access) {
            access = a_access;
        }

        Access getAccess() {
            return access;
        }

        void setType(const llvm::Type* typ) {
            type = typ;
        }

        const llvm::Type* getType() {
            return type;
        }

        inline bool hasParent() {
            return has_parent;
        }

        // void clone() {
        //     unsigned int new_ID = ++global_object_id;
        //     parent_ID = ID;
        //     ID = new_ID;
        // }

        bool equals(std::string s) {
            return s == toString(false);
        }

        bool operator==(const AccessType& other) const {
            if (other.fields != fields)
                return false;
            if (other.access != access)
                return false;
            if (other.type != type)
                return false;
            return true;
        }

        std::string dumpICFGNodes() const {

            std::string str;
            raw_string_ostream rawstr(str);

            for (auto inst: getICFGNodes())
                rawstr << inst->toString() << "; \n";
            rawstr << "\n";

            return rawstr.str();
        }

        std::string toStringParent() {
            std::string str;
            raw_string_ostream rawstr(str);

            // example of output:
            // (., write) -> write the whole pointer (all the fields)
            // (.1, read) -> read field in position 1
            // (.0.1, write) -> write subfield 1 of the field 0

            rawstr << "(.";
            int max_fields = getNumFields();
            int i = 0;
            for (int f: getFields()) {
                if (f == -1)
                    rawstr << "*";
                else 
                    rawstr << f;
                if (i < max_fields - 1)
                    rawstr << ".";
                i++;
            }

            rawstr << ", ";
            if (access == Access::read) 
                rawstr << "read";
            else if (access == Access::write)
                rawstr << "write";
            else if (access == Access::ret)
                rawstr << "return";
            else if (access == Access::none)
                rawstr << "none";
            else if (access == Access::del)
                rawstr << "delete";
            else if (access == Access::create)
                rawstr << "create";
            else {
                outs() << "[ERROR] Access:: " << access << " unknown!!\n";
                exit(1);
            }
            rawstr << ", " << type_to_string(type);
            rawstr << ", " << type_to_hash(type) << ")";

            return rawstr.str();
        }

        std::string toString(bool verbose = false) {

            std::string str;
            raw_string_ostream rawstr(str);

            // example of output:
            // (., write) -> write the whole pointer (all the fields)
            // (.1, read) -> read field in position 1
            // (.0.1, write) -> write subfield 1 of the field 0

            rawstr << "(";

            if (has_parent) {
                AccessType p(p_type);
                // AccessType p;
                // p.setType(p_type);
                p.setAccess(p_access);
                for (auto f: p_fields)
                    p.addField(f);
                rawstr << p.toStringParent() << ",";
            } else 
                rawstr << "(0),";

            rawstr  << ".";
            int max_fields = getNumFields();
            int i = 0;
            for (int f: getFields()) {
                if (f == -1)
                    rawstr << "*";
                else 
                    rawstr << f;
                if (i < max_fields - 1)
                    rawstr << ".";
                i++;
            }

            rawstr << ", ";
            if (access == Access::read) 
                rawstr << "read";
            else if (access == Access::write)
                rawstr << "write";
            else if (access == Access::ret)
                rawstr << "return";
            else if (access == Access::none)
                rawstr << "none";
            else if (access == Access::del)
                rawstr << "delete";
            else if (access == Access::create)
                rawstr << "create";
            else {
                outs() << "[ERROR] Access:: " << access << " unknown!!\n";
                exit(1);
            }
            rawstr << ", " << type_to_string(type);
            rawstr << ", " << type_to_hash(type) << ")";

            if (verbose) {
                rawstr << "\n";
                rawstr << dumpICFGNodes();
            }

            return rawstr.str();
        }

        Json::Value dumpICFGNodesJson() const {

            Json::Value debugInfo(Json::arrayValue);

            // for (auto inst: getICFGNodes())
            //     debugInfo.append(inst->toString());

            return debugInfo;
        }

        Json::Value toJsonParent() {
            Json::Value accessTypeJson;

            if (access == Access::read) 
                accessTypeJson["access"] = "read";
            else if (access == Access::write)
                accessTypeJson["access"] = "write";
            else if (access == Access::ret)
                accessTypeJson["access"] = "return";
            else  if (access == Access::none)
                accessTypeJson["access"] = "none";
            else if (access == Access::del)
                accessTypeJson["access"] = "delete";
            else if (access == Access::create)
                accessTypeJson["access"] = "create";
            else {
                outs() << "[ERROR] Access:: " << access << " unknown!!\n";
                exit(1);
            }

            Json::Value fieldsJson(Json::arrayValue);

            for (auto field: fields)
                fieldsJson.append(field);
        
            accessTypeJson["fields"] = fieldsJson;
            accessTypeJson["type"] = type_to_hash(type);
            accessTypeJson["type_string"] = type_to_string(type);

            return accessTypeJson;
        }

        Json::Value toJson(bool verbose) {
            Json::Value accessTypeJson;

            if (has_parent) {
                AccessType p(p_type);
                // AccessType p;
                // p.setType(p_type);
                p.setAccess(p_access);
                for (auto f: p_fields)
                    p.addField(f);
                accessTypeJson["parent"] = p.toJsonParent();
            } else 
                accessTypeJson["parent"] = 0;

            if (access == Access::read) 
                accessTypeJson["access"] = "read";
            else if (access == Access::write)
                accessTypeJson["access"] = "write";
            else if (access == Access::ret)
                accessTypeJson["access"] = "return";
            else  if (access == Access::none)
                accessTypeJson["access"] = "none";
            else if (access == Access::del)
                accessTypeJson["access"] = "delete";
            else if (access == Access::create)
                accessTypeJson["access"] = "create";
            else {
                outs() << "[ERROR] Access:: " << access << " unknown!!\n";
                exit(1);
            }

            Json::Value fieldsJson(Json::arrayValue);

            for (auto field: fields)
                fieldsJson.append(field);
        
            accessTypeJson["fields"] = fieldsJson;
            accessTypeJson["type"] = type_to_hash(type);
            accessTypeJson["type_string"] = type_to_string(type);

            if (verbose)
                accessTypeJson["debug"] = dumpICFGNodesJson();

            return accessTypeJson;
        }

        // for std:set
        bool operator<(const AccessType& rhs) const {
            if (fields == rhs.fields) {
                if (access == rhs.access)
                    return type < rhs.type;
                else
                    return access < rhs.access;
            }
            
            return fields < rhs.fields;
        }
};



class AccessTypeSet {
    private:
        // std::map<AccessType, std::set<const ICFGNode*>> ats;
        std::set<AccessType> ats_set;

    public:
        void insert(AccessType at, const ICFGNode* inst) {
            // outs() << "[DEBUG] insert: " << at.toString() << "\n";

            // at is already in the set
            auto at_iter = ats_set.find(at);
            if (at_iter != ats_set.end()) {
                AccessType at_prev = *at_iter;
                at_prev.addICFGNode(inst);
                ats_set.erase(at_prev);
                ats_set.insert(at_prev);
            } else {
                at.addICFGNode(inst);
                ats_set.insert(at);
            }
        }

        void remove(AccessType at) {
            auto at_iter = ats_set.find(at);
            if (at_iter != ats_set.end()) {
                ats_set.erase(*at_iter);
            }
        }

        size_t size() const {
            return ats_set.size();
        }

        std::set<const ICFGNode*> getAllICFGNodes() const {
            std::set<const ICFGNode*> allNodes;

            for (auto at: ats_set) {
                for (auto icfg_node: at.getICFGNodes()) {
                    allNodes.insert(icfg_node);
                }
            }

            return allNodes;
        }

        Json::Value toJson(bool verbose) {
            Json::Value result(Json::arrayValue);

            for (auto at: ats_set) 
                result.append(at.toJson(verbose));

            return result;
        }

        std::string toString(bool verbose = false) {
            std::stringstream sstream;

            for (auto at: ats_set) 
                sstream << at.toString(verbose) << std::endl;

            return sstream.str();
        }

        std::set<AccessType>::iterator begin() const {
            return ats_set.begin(); 
        }

        std::set<AccessType>::iterator end() const {
            return ats_set.end();
        }

        bool operator<(const AccessTypeSet& rhs) const {
            return ats_set < rhs.ats_set;
        }    

};

class Path {
    private:
        const VFGNode* node;
        AccessType access_type;
        const Value* prevValue;
        std::stack<const CallICFGNode*> stack;
        std::vector<std::pair<const ICFGNode*, AccessType>> history;

    public:
        // Path(const VFGNode* p_node) {
        //     node = p_node;
        //     prevValue = nullptr;
        // }

        Path(const VFGNode* p_node, const llvm::Value* val, const llvm::Type* type) :
            access_type(type) {
            node = p_node;
            prevValue = nullptr;
            // access_type.setType(val->getType());
        }

        void addStep(const ICFGNode* node) {
            history.push_back(std::make_pair(node, getAccessType()));
        }

        const std::vector<std::pair<const ICFGNode*, AccessType>> getSteps() {
            return history;
        }

        const Value* getPrevValue() {
            return prevValue;
        }

        void setPrevValue(const Value* a_prevValue) {
            prevValue = a_prevValue;
        }

        const VFGNode* getNode() {
            return node;
        }

        void setNode(const VFGNode* a_node) {
            node = a_node;
        }

        AccessType getAccessType() {return access_type;}

        void setAccessType(AccessType a_access_type) {
           access_type = a_access_type;
        }

        bool isCorrect(const CallICFGNode* edge) {
            if (getStackSize() == 0)
                return false;
            return stack.top() == edge;
        }

        const CallICFGNode* topFrame() {
            if (getStackSize() == 0)
                return nullptr;
            return stack.top();
        }

        void pushFrame(const CallICFGNode* cs) {
            stack.push(cs);
        }

        void popFrame() {
            stack.pop();
        }

        uint getStackSize() {return stack.size();}
        
        void dump() {
            // for (auto n: get_full_path()) {
            //     outs() << n->toString() << "\n";
            // }
            outs() << "<TBI>!!\n";
        }

        void dump_stack() {
            auto stk_copy(this->stack);
            while(!stk_copy.empty()) {
                auto f = stk_copy.top();
                outs() << f->toString() << "\n";
                stk_copy.pop();
            }
        }

        // for using it in std::set
        bool operator<(const Path& rhs) const 
        {
            if (node == rhs.node)
                return  access_type < rhs.access_type;
            else
                return node < rhs.node;
        }

        // copy assignment operator
        Path& operator=(const Path &rhs) {
            this->node = rhs.node;
            this->access_type = rhs.access_type;
            this->stack = rhs.stack;

            this->history = rhs.history;

            return *this;
        };

        std::string toString() {

            std::string str;
            raw_string_ostream rawstr(str);

            rawstr << "<" << access_type.toString() << ", ";
            rawstr << node->toString() << ">";

            return rawstr.str();
        }
};

class ValueMetadata {
    AccessTypeSet ats;
    bool is_array;
    bool is_malloc_size;
    bool is_file_path;
    std::string len_depends_on;
    std::vector<std::string> set_by;

    const llvm::Value* val;
    std::vector<llvm::Value*> indexes;
    std::vector<std::pair<llvm::Value*, Path>> fun_params;

    public: 
        ValueMetadata() {
            val = nullptr;
            is_array = false;
            is_malloc_size = false;
            is_file_path = false;
            len_depends_on = "";
        }

        void setValue(const llvm::Value* p_val) {val = p_val;}
        const llvm::Value* getValue() {return val;}

        void addIndex(const llvm::Value* idx) {
            indexes.push_back(const_cast<llvm::Value*>(idx));
        }
        std::vector<llvm::Value*> getIndexes() {return indexes;}

        void addFunParam(const llvm::Value* fp, Path *pp) {
            auto fp_v = const_cast<llvm::Value*>(fp);
            if (pp == nullptr) {
                Path p(nullptr, nullptr, nullptr);
                auto el = std::make_pair(fp_v, p);
                fun_params.push_back(el);
            } else {
                auto el = std::make_pair(fp_v, *pp);
                fun_params.push_back(el);
            }
        }
        std::vector<std::pair<llvm::Value*, Path>> getFunParams() {
            return fun_params;
        }

        void setAccessTypeSet(AccessTypeSet p_ats) {ats = p_ats;}
        AccessTypeSet* getAccessTypeSet() {return &ats;}
        int getAccessNum() {return ats.size();}

        void setIsArray(bool p_is_array) {is_array = p_is_array;}
        bool isArray() {return is_array;}

        void setMallocSize(bool p_malloc_size) {is_malloc_size = p_malloc_size;}
        bool isMallocSize() {return is_malloc_size;}

        void setIsFilePath(bool p_is_file_path) {is_file_path = p_is_file_path;}
        bool isFilePath() {return is_file_path;}

        void setLenDependency(std::string p_dep) {len_depends_on = p_dep;}
        std::string getLenDependency() {return len_depends_on;}

        void addSetByDependency(std::string p_dep) {set_by.push_back(p_dep);}
        std::vector<std::string> getSetByDependency() {return set_by;}


        Json::Value toJson(bool verbose) {

            Json::Value medataResult;

            medataResult["access_type_set"] = ats.toJson(verbose);
            medataResult["is_array"] = this->is_array;
            medataResult["is_malloc_size"] = this->is_malloc_size;
            medataResult["is_file_path"] = this->is_file_path;
            medataResult["len_depends_on"] = this->len_depends_on;

            Json::Value setByJson(Json::arrayValue);
            for (auto d: this->set_by)
                setByJson.append(d);

            medataResult["set_by"] = setByJson;

            return medataResult;
        }

        std::string toString(bool verbose) {

            std::stringstream sstream;

            sstream << "is_array: " << std::to_string(this->is_array) << "\n";
            sstream << "is_malloc_size: " 
                    << std::to_string(this->is_malloc_size) << "\n";
            sstream << "is_file_path: " 
                    << std::to_string(this->is_file_path) << "\n";
            sstream << "len_depends_on: " << this->len_depends_on << "\n";

            std::string set_by_str = "";
            for (auto d: this->set_by)
                set_by_str += d + " ";

            sstream << "set_by: " << set_by_str << "\n";
            sstream << "access_type_set:\n" << ats.toString(verbose) << "\n";

            return sstream.str();
        }

        std::string getSummary() {

            std::stringstream sstream;

            sstream << "ATS " << this->ats.size() << ", ";
            sstream << "array " << std::to_string(this->is_array) << ", ";
            sstream << "malloc " << std::to_string(this->is_malloc_size) << ", ";
            sstream << "path " << std::to_string(this->is_file_path) << ", ";
            sstream << "depends '" << len_depends_on << "'\n";

            return sstream.str();
        }

        // // copy assignment operator
        // ValueMetadata& operator=(const ValueMetadata &rhs) {

        //     this->val = rhs.val;
        //     this->is_array = rhs.is_array;
        //     this->is_malloc_size = rhs.is_malloc_size;
        //     this->is_file_path = rhs.is_file_path;
        //     this->len_depends_on = rhs.len_depends_on;

        //     // this->fields = rhs.fields;
        //     // this->access = rhs.access;
        //     // this->type = rhs.type;

        //     // // hope this does not make a mess!
        //     // this->icfg_set = rhs.icfg_set;

        //     // // parent
        //     // this->has_parent = rhs.has_parent;
        //     // this->p_fields = rhs.p_fields;
        //     // this->p_access = rhs.p_access;
        //     // this->p_type = rhs.p_type;

        //     // // visited types for GEP recursion
        //     // this->visited_types = rhs.visited_types;

        //     return *this;
        // };

    public: // static functions/data!

        // handle debug information
        static bool debug;
        static std::string debug_condition;
        static bool consider_indirect_calls;

        typedef std::map<const CallICFGNode *, std::set<const SVFFunction*>> MyCallEdgeMap;

        static MyCallEdgeMap myCallEdgeMap_inst;

        static ValueMetadata extractParameterMetadata(
            const SVFG*, const Value*, const Type*);
        static ValueMetadata extractReturnMetadata(
            const SVFG*, const Value*);
        static std::string extractLenDependencyParameter(
            const SVF::SVFVar*, ValueMetadata*, SVF::SVFG*, const SVFFunction*);
        static std::vector<std::string> extractDependencyAmongParameters(
            const SVF::SVFVar*, ValueMetadata*, SVF::SVFG*, const SVFFunction*);
};

class FunctionConditions {
    private:
        // std::vector<AccessTypeSet> parameter_ats;
        // AccessTypeSet return_ats;
        std::vector<ValueMetadata> parameter_metadata;
        ValueMetadata return_metadata;
        std::string function_name;

    public:
        void setFunctionName(std::string f) {function_name = f;}
        std::string getFunctionName() {return function_name;}

        void addParameterMetadata(ValueMetadata par) {
            parameter_metadata.push_back(par);
        }

        int getParameterNum() {return parameter_metadata.size();}

        void replaceParameterMetadata(int parm, ValueMetadata new_par) {
            parameter_metadata[parm] = new_par;
        }

        ValueMetadata getParameterMetadata(int idx) {
            if (idx < 0 || idx >= parameter_metadata.size())
                assert("idx out of bounds!");

            return parameter_metadata[idx];
        }

        void setReturnMetadata(ValueMetadata ret) {return_metadata = ret;}
        ValueMetadata getReturnMetadata() {return return_metadata;}

        // for using it in std::set
        bool operator<(const FunctionConditions& rhs) const 
        {
            return function_name < rhs.function_name;
        }

        Json::Value toJson(bool verbose) {

            Json::Value functionResult;

            functionResult["function_name"] = function_name;

            int pn = 0;
            for (auto param: parameter_metadata) {
                auto param_key = "param_" + std::to_string(pn);
                functionResult[param_key] = param.toJson(verbose);
                pn++;
        std::vector<ValueMetadata> parameter_metadata;
            }

            functionResult["return"] = return_metadata.toJson(verbose);

            return functionResult;
        }

        std::string toString(bool verbose) {

            std::stringstream sstream;

            sstream << "Function: " << function_name << "\n";

            int pn = 0;
            for (auto param: parameter_metadata) {
                sstream << "param_" + std::to_string(pn) << ":\n";
                sstream << param.toString(verbose);
                pn++;
            }

            sstream << "return:\n";
            sstream << return_metadata.toString(verbose);

            return sstream.str();
        }
        std::string getSummary() {
            std::stringstream sstream;

            sstream << "[INFO] Summary " << function_name << ":\n";

            int pn = 0;
            for (auto param: parameter_metadata) {
                sstream << "param_" + std::to_string(pn) 
                        << ": " << param.getAccessNum() << " access types\n";
                pn++;
            }

            sstream << "return: " << return_metadata.getAccessNum()
                    << " access types\n";

            return sstream.str();
        }
};

class FunctionConditionsSet {
    private:
        std::map<std::string, FunctionConditions> fun_cond_set;
    public:
        void addFunctionConditions(FunctionConditions fun_cond) {
            fun_cond_set.insert(
                std::pair<std::string, FunctionConditions>
                    (fun_cond.getFunctionName(),fun_cond)
            );
        }

        Json::Value toJson(bool verbose) {
            Json::Value funCondJson(Json::arrayValue);

            for (auto fc: fun_cond_set)
                funCondJson.append(fc.second.toJson(verbose));

            return funCondJson;
        }

        std::string toString(bool verbose) {

            std::stringstream sstream;

            for (auto fc: fun_cond_set)
                sstream << fc.second.toString(verbose);

            return sstream.str();
        }

        std::string getSummary() {
            std::stringstream sstream;

            for (auto fc: fun_cond_set)
                sstream << fc.second.getSummary();

            return sstream.str();
        }

    public: // static functions
        static void storeIntoJsonFile(FunctionConditionsSet,
            std::string, bool);
        static void storeIntoTextFile(FunctionConditionsSet,
            std::string, bool);
};

#endif /* INCLUDE_DOM_ACCESSTYPE_H_ */
