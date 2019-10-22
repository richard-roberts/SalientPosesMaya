#include <iomanip>
#include <sstream>
#include <vector>

#include <maya/MGlobal.h>
#include <maya/MArgDatabase.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MFnDagNode.h>
#include <maya/MPlug.h>
#include <maya/MPlugArray.h>
#include <maya/MItSelectionList.h>
#include <maya/MAnimUtil.h>
#include <maya/MFnAnimCurve.h>
#include <maya/MTime.h>
#include <maya/MFnIntArrayData.h>
#include <maya/MDataHandle.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MAngle.h>

#include "SelectCommand.hpp"
#include "MayaUtils.hpp"
#include "../SalientPosesPerformance/src/ErrorTable.hpp"
#include "../SalientPosesPerformance/src/Selector.hpp"


#define VERBOSE 0

const char* SelectCommand::kName = "salientSelect";

MStatus SelectCommand::doIt(const MArgList& args) {
    MStatus status;
    
    status = GatherCommandArguments(args);
	if (status != MS::kSuccess) {
		return MS::kFailure;
	}
    
    // Ensure the start and end frames are given as argumetns
    if (fStart == -1 || fEnd == -1) {
        std::ostringstream os;
        os << "The start and end flags have not been set (start=" << fStart << " end=" << fEnd << ")";
        Log::error(os.str());
        return MS::kFailure;
    }
    
    if (VERBOSE == 1) {
        std::ostringstream os;
        os << "Start: " << fStart << std::endl;
        os << "End: " << fEnd << std::endl;
        os << "Data: " << std::endl;
        os << fAnimData << std::endl;
        MGlobal::displayInfo(os.str().c_str());
    }
    
    // Perform the selection
    AnimationProxy anim = AnimationProxy(fAnimData);
    ErrorTable table = ErrorTable(anim);
    SelectionProxy selections = Select::upToN(fEnd - fStart + 1, fMaxKeyframes, anim, table);
    
    if (VERBOSE == 2) {
        std::ostringstream os;
        for (int i = 3; i < fMaxKeyframes + 1; i++) {
            std::vector<int> sel = selections.getSelectionByNKeyframes(i);
            os << i << ": ";
            for (int j = 0; j < sel.size(); j++) {
                os << sel[j] << ",";
            }
            os << std::endl;
        }
        MGlobal::displayInfo(os.str().c_str());
    }

    // Build string containing result (precise to four decimal places)
    std::ostringstream ret;
    ret << std::setprecision(4) << std::fixed;

    // Pipe in pairs of error and selection in the form:
    //   e|a,b,c
    //     where e is error, | is a delimiter, and a,b,c are the selection (wthout spaces).
    // Each error-selection pair is delimited by a new line.
    for (int i = 3; i < fMaxKeyframes + 1; i++) {
        float error = selections.getErrorByNKeyframes(i);
        std::vector<int> selection = selections.getSelectionByNKeyframes(i);
        ret << error << "|";
        ret << selection[0];
        for (int j = 1; j < selection.size(); j++) ret << "," << selection[j];
        ret << "\n";
    }

	setResult(MString(ret.str().c_str()));
    return MS::kSuccess;
}

MStatus SelectCommand::GatherCommandArguments(const MArgList& args) {

	if (args.length() != 4) {
		MGlobal::displayError("You must provide 4 arguments: start, end, maxKeyframes, animData (list).");
		return MS::kFailure;
	}

    unsigned int ix = 0;
	fStart = args.asInt(ix++);
	fEnd = args.asInt(ix++);
	fMaxKeyframes = args.asInt(ix++);
    
    MDoubleArray mAnimData = args.asDoubleArray(ix);
    int nFrames = fEnd - fStart + 1;
    int nDims = mAnimData.length() / nFrames;
    fAnimData = Eigen::MatrixXf(nDims, nFrames);
    int f = 0;
    int d = 0;
	for (uint i = 0; i < mAnimData.length(); i++) {
		fAnimData(d, f) = mAnimData[i];
        d += 1;
        if (d == nDims) { d = 0; f += 1; }
	}
    
    return MS::kSuccess;
}

