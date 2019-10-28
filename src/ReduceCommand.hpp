#pragma once

#include <vector>

#include <maya/MArgList.h>
#include <maya/MSyntax.h>
#include <maya/MPxCommand.h>
#include <maya/MSelectionList.h>


class ReduceCommand : public MPxCommand {
public:
    virtual MStatus  doIt(const MArgList& args);
    virtual bool isUndoable() const { return false; }
    static void* creator() { return new ReduceCommand; }
	const static char* kName;
	
private:
    MStatus GatherCommandArguments(const MArgList& args);
    
	MString fObjectName;
	MString fAttrName; 
	std::vector<int> fKeyframes;
	Eigen::MatrixXf fAnimData; 
};
