#ifndef GLOBALSTRUCTANALYSIS_H_
#define GLOBALSTRUCTANALYSIS_H_

#include "FastCluster/fastcluster.h"
#include "Graphs/SVFGOPT.h"
#include "MemoryModel/PointerAnalysisImpl.h"
#include "MemoryModel/PointerAnalysis.h"
#include "MSSA/SVFGBuilder.h"
#include "WPA/WPAFSSolver.h"

using namespace SVF;
using namespace SVFUtil;

class GlobalStruct : public FlowSensitive
{

public:
    /// Constructor
    explicit GlobalStruct(SVFIR* _pag): FlowSensitive(_pag) { }

    /// Destructor
    ~GlobalStruct() override = default;

    /// Create single instance of flow-sensitive pointer analysis
    static GlobalStruct* createSGWPA(SVFIR* _pag)
    {
        if (gspta == nullptr)
        {
            gspta = std::unique_ptr<GlobalStruct>(new GlobalStruct(_pag));
            gspta->analyze();
        }
        return gspta.get();
    }

    /// Release flow-sensitive pointer analysis
    static void releaseFSWPA()
    {
        gspta = nullptr;
    }

    /// We start from here
    virtual bool runOnModule(SVFModule*)
    {
        return false;
    }

    /// GlobalStruct analysis
    void analyze() override;

    /// Initialize analysis
    void initialize() override;

    /// Finalize analysis
    void finalize() override;


protected:
    static std::unique_ptr<GlobalStruct> gspta;


    void get_function_pointers(const llvm::Value*,
            std::map<std::string, std::set<const llvm::Function*>>*);
};

#endif /* GLOBALSTRUCTANALYSIS_H_ */