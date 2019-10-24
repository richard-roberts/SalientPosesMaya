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
#include "../SalientPosesPerformance/src/SelectionManager.hpp"


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
		os << "Error Type: " << fErrorType << std::endl;
        os << "Start: " << fStart << std::endl;
        os << "End: " << fEnd << std::endl;
		os << "Fixed Keyframes: ";
		for (int i = 0; i < fFixedKeyframes.size(); i++) { os << fFixedKeyframes[i] << ","; } os << std::endl;
        os << "Data: " << std::endl;
        os << fAnimData << std::endl;
        MGlobal::displayInfo(os.str().c_str());
    }
    
    // Perform the selection
    AnimationProxy anim = AnimationProxy(fAnimData);
	anim = anim.subAnimation(fStart, fEnd);

	/*ErrorTable table;
	if (fErrorType == "line") {
		table = ErrorTable::usingLineBasedError(anim);
	} else if (fErrorType == "curve") {
		table = ErrorTable::usingCurveBasedError(anim);
	} else {
		std::ostringstream os;
		os << "The error type `" << fErrorType << "` is invalid? This shouldn't happen!" << std::endl;
		MGlobal::displayError(os.str().c_str());
	}

    SelectionProxy selections = Select::upToN(anim, table, fMaxKeyframes);*/

	SelectionManager manager(fErrorType.asChar(), anim, fFixedKeyframes);
	manager.incrementUntilNKeyframes(fMaxKeyframes);
	SelectionProxy selections = manager.getFinalSelectionProxy();
    
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
    for (int i = selections.getMinKeyframes(); i < selections.getMaxKeyframes() + 1; i++) {
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

	if (args.length() != 6) {
		std::ostringstream os;
		os << std::endl;
		os << "----------------------------------------------" << std::endl; 
		os << "Invalid args" << std::endl;
		os << "-----------" << std::endl;
		os << "You must provide 5 arguments:" << std::endl;
		os << "    1. error type (`line` or `curve`)" << std::endl;
		os << "    2. start (int, frame number)" << std::endl;
		os << "    3. end (int, frame number)" << std::endl; 
		os << "    4. max number of keyframes (int)" << std::endl;
		os << "    5. fixed keyframes (list of ints)." << std::endl;
		os << "    6. the animation data (list of floats, pose-by-pose)." << std::endl;
		os << "----------------------------------------------" << std::endl;
		MGlobal::displayError(os.str().c_str());
		return MS::kFailure;
	}

    unsigned int ix = 0;
	fErrorType = args.asString(ix++);

	if (fErrorType != "line" && fErrorType != "curve") {
		std::ostringstream os;
		os << "The error type `" << fErrorType << "` is not understand, must be either `line` or `curve`" << std::endl;
		MGlobal::displayError(os.str().c_str());
		return MS::kFailure;
	}

	fStart = args.asInt(ix++);
	fEnd = args.asInt(ix++);
	int nFrames = fEnd - fStart + 1;
	fMaxKeyframes = args.asInt(ix++);

	if (fMaxKeyframes > nFrames) {
		std::ostringstream os;
		os << "You cannot select more keyframes than there are frames" << std::endl;
		MGlobal::displayError(os.str().c_str());
		return MS::kFailure;
	}
    
	MIntArray mFixedKeyframes = args.asIntArray(ix);
	fFixedKeyframes = std::vector<int>();
	for (uint i = 0; i < mFixedKeyframes.length(); i++) {
		fFixedKeyframes.push_back(mFixedKeyframes[i]);
	}

	ix += 1;

    MDoubleArray mAnimData = args.asDoubleArray(ix);
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

