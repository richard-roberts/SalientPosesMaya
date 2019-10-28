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

#include "../eigen-git-mirror/Eigen/Eigen"

#include "../SalientPosesPerformance/src/Interpolator.hpp"
#include "MayaUtils.hpp"
#include "ReduceCommand.hpp"


#define VERBOSE 0

const char* ReduceCommand::kName = "salientReduce";

MStatus ReduceCommand::doIt(const MArgList& args) {
    MStatus status;
	
	// Get basic stuff
	MTime::Unit timeUnit = MayaConfig::getCurrentFPS();
	MAngle::Unit angleUnit = MayaConfig::getCurrentAngleUnit();
    
    // Process arguments
    status = GatherCommandArguments(args);
	if (status != MS::kSuccess) {
		return MS::kFailure;
	}

	if (VERBOSE == 1) {
		std::ostringstream os;
		os << "Object: " << fObjectName << std::endl;
		os << "Attribute: " << fAttrName << std::endl;
		os << "Keyframes: ";
		for (int i = 0; i < fKeyframes.size(); i++) {
			os << fKeyframes[i] << ",";
		}
		os << std::endl;
		MGlobal::displayInfo(os.str().c_str());
	}

    std::vector<HighDimCubic> cubics = Interpolate::optimal(fAnimData, fKeyframes);

	MDoubleArray values;
	for (int i = 0; i < cubics.size(); i++) {
		values.append(cubics[i].p1[0]);
		values.append(cubics[i].p1[1]);
		values.append(cubics[i].p2[0]);
		values.append(cubics[i].p2[1]);
		values.append(cubics[i].p3[0]);
		values.append(cubics[i].p3[1]);
		values.append(cubics[i].p4[0]);
		values.append(cubics[i].p4[1]);
	}
	setResult(values);
    return MS::kSuccess;
}

MStatus ReduceCommand::GatherCommandArguments(const MArgList& args) {

	if (args.length() != 4) {
		MGlobal::displayError("You must provide 4 arguments: object name, attribute name, keyframes (list, int), anim data (list, float).");
		return MS::kFailure;
	}

	unsigned int ix = 0;
	fObjectName = args.asString(ix++);
	fAttrName = args.asString(ix++);

	MIntArray mSelection = args.asIntArray(ix); ix += 1;
	fKeyframes.clear();
	for (uint i = 0; i < mSelection.length(); i++) {
		fKeyframes.push_back(mSelection[i]);
	}

	MDoubleArray mAnimData = args.asDoubleArray(ix); ix += 1;
	int nDims = 2;
	int nFrames = mAnimData.length() / nDims;
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

