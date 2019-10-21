#pragma once

#include <vector>

#include <maya/MArgList.h>
#include <maya/MSyntax.h>
#include <maya/MPxCommand.h>
#include <maya/MSelectionList.h>


class ReduceCommand : public MPxCommand {
public:
    ReduceCommand() {}
    virtual MStatus  doIt(const MArgList& args);
    virtual MStatus  undoIt() { return MS::kSuccess; }
    virtual MStatus  redoIt() { return MS::kSuccess; }
    virtual bool isUndoable() const { return false; }
    static void* creator() { return new ReduceCommand; }
    static MSyntax newSyntax();
    
    const static char* kName;
    const static char* kSelectionFlagShort;
    const static char* kSelectionFlagLong;
    
private:
    MStatus GatherCommandArguments(const MArgList& args);
    
    std::vector<int> selection;
    
};
