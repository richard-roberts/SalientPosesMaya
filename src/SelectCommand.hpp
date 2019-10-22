#pragma once

#include <vector>

#include "../eigen-git-mirror/Eigen/Dense"

#include <maya/MArgList.h>
#include <maya/MSyntax.h>
#include <maya/MPxCommand.h>
#include <maya/MSelectionList.h>


class SelectCommand : public MPxCommand {
public:
    virtual MStatus  doIt(const MArgList& args);
    virtual bool isUndoable() const { return false; }
    static void* creator() { return new SelectCommand; }
    const static char* kName;
    
private:
    MStatus GatherCommandArguments(const MArgList& args);
    
    int fStart;
    int fEnd;
	int fMaxKeyframes;
    Eigen::MatrixXf fAnimData;
    
};
