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
    
	// Get MPlug by searching through animated plugs connected to the object
	// (specified by fObjectName) and find the one matching the attribute in
	// question (specified by fAttributeName).
	MObject mObject;
	MSelectionList selList;
	MPlugArray plugs;
	int matchingPlugIndex = -1;
	selList.add(fObjectName);
	selList.getDependNode(0, mObject);
	MAnimUtil::findAnimatedPlugs(mObject, plugs);
	for (int i = 0; i < plugs.length(); i++) {
		MPlug plug = plugs[i];
		if (plug.partialName() == fAttrName) {
			matchingPlugIndex = i;
			break;
		}
	}

	// Fail if not animate plug found
	if (matchingPlugIndex == -1) {
		std::ostringstream os; os << "did not find a plug matching " << fObjectName.asChar() << "." << fAttrName.asChar();
		MGlobal::displayError(os.str().c_str());
		return MS::kFailure;
	}

	// Get the curve and gather info
	MFnAnimCurve mCurve(plugs[matchingPlugIndex]);    
    int start = fKeyframes[0];
    int finish = fKeyframes[fKeyframes.size() - 1];
    int nFrames = finish - start + 1;
    bool usingDegrees = angleUnit == MAngle::kDegrees;
    bool isAngluar = mCurve.animCurveType() == MFnAnimCurve::kAnimCurveTA;
            
    // Cache the curve data
    Eigen::VectorXf data(nFrames);
    for (int i = 0; i < nFrames; i++) {
        MTime time((double) (start + i), timeUnit);
        float v = mCurve.evaluate(time); 
        if (isAngluar && usingDegrees) {
            data[i] = v * 57.2958279088;
        } else {
            data[i] = v;
        }                
    }

    std::string name = mCurve.name().asChar();
    std::vector<Cubic> cubics = Interpolate::optimal(data, fKeyframes);

	MDoubleArray values;
	for (int i = 0; i < cubics.size(); i++) {
		values.append(cubics[i].p1x());
		values.append(cubics[i].p1y());
		values.append(cubics[i].p2x());
		values.append(cubics[i].p2y());
		values.append(cubics[i].p3x());
		values.append(cubics[i].p3y());
		values.append(cubics[i].p4x());
		values.append(cubics[i].p4y());
	}
	setResult(values);
    return MS::kSuccess;
}

MStatus ReduceCommand::GatherCommandArguments(const MArgList& args) {

	if (args.length() != 3) {
		MGlobal::displayError("You must provide 3 arguments: start, end, keyframes (list).");
		return MS::kFailure;
	}

	unsigned int ix = 0;
	fObjectName = args.asString(ix++);
	fAttrName = args.asString(ix++);

	MIntArray mSelection = args.asIntArray(ix);
	fKeyframes.clear();
	for (uint i = 0; i < mSelection.length(); i++) {
		fKeyframes.push_back(mSelection[i]);
	}

    return MS::kSuccess;
}

