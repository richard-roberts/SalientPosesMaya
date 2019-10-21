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


// Set name and flags
const char* ReduceCommand::kName = "salientReduce";
const char* ReduceCommand::kSelectionFlagShort = "-sel";
const char* ReduceCommand::kSelectionFlagLong = "-selection";

MStatus ReduceCommand::doIt(const MArgList& args) {
    MStatus status;
    
    // Process arguments
    status = GatherCommandArguments(args);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    
    // Get current selection
    MSelectionList slist;
    MGlobal::getActiveSelectionList(slist);
    MItSelectionList iter(slist, MFn::kInvalid, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    
    // Ensure at least 1 thing is selected
    int n = slist.length();
    if (n == 0) {
        Log::error("Please select objects for reduction");
        return MS::kFailure;
    }
    
    // Ensure the selection contains at least two keyframes
    if (selection.size() < 2) {
        Log::error("At least two keyframes must be selected.");
        return MS::kFailure;
    }
    
    int start = selection[0];
    int finish = selection[selection.size() - 1];
    int nFrames = finish - start + 1;
    MTime::Unit timeUnit = MayaConfig::getCurrentFPS();
    MAngle::Unit angleUnit = MayaConfig::getCurrentAngleUnit();
    bool usingDegrees = angleUnit == MAngle::kDegrees;
    
    while (!iter.isDone()) {
        MObject mobj;
        iter.getDependNode(mobj);
        iter.next();
        
        // Find animated plugs connected to this node
        MFnDependencyNode dependNode(mobj);
        MPlugArray plugs;
        MAnimUtil::findAnimatedPlugs(mobj, plugs);
        
        // Iterate through each curve
        for (int k = 0; k < plugs.length(); k++) {
            MFnAnimCurve curve(plugs[k]);
            
            bool isAngluar = curve.animCurveType() == MFnAnimCurve::kAnimCurveTA;
            
            // Cache the curve data
            Eigen::VectorXf data(nFrames);
            for (int i = 0; i < nFrames; i++) {
                MTime time((double) (start + i), timeUnit);
                float v = curve.evaluate(time);
                
                if (isAngluar && usingDegrees) {
                    data[i] = v * 57.2958279088;
                } else {
                    data[i] = v;
                }
                
            }
            
            std::string name = curve.name().asChar();
            std::vector<Cubic> cubics = Interpolate::optimal(data, selection);
            
            // Remove non-keyframes
            for (int j = start; j < finish; j++) {
                bool j_in_sel = std::find(selection.begin(), selection.end(), j) != selection.end();
                if (!j_in_sel) {
                    MTime t((double) j,timeUnit);
                    unsigned int ix = curve.findClosest(t);
                    curve.remove(ix);
                }
            }
            
            // Update tangents based on fitting
            for (int i = 0; i < selection.size() - 1; i++) {
                Cubic cubic = cubics.at(i);
                int s = selection[i];
                int e = selection[i + 1];
                
                // Set outgoing for left keyframe
                uint ixLeft;
                MTime timeLeft((double) s, timeUnit);
                curve.find(timeLeft, ixLeft);
                curve.setWeightsLocked(ixLeft, false);
                curve.setTangentsLocked(ixLeft, false);
                curve.setAngle(ixLeft, MAngle(cubic.angleLeft(), MAngle::kRadians), false);
                curve.setWeight(ixLeft, cubic.weightLeft(), false);
                
                // Set incoming for right keyframe
                uint ixRight;
                MTime timeRight((double) e, timeUnit);
                curve.find(timeRight, ixRight);
                curve.setWeightsLocked(ixRight, false);
                curve.setTangentsLocked(ixRight, false);
                
                curve.setAngle(ixRight, MAngle(cubic.angleRight(), MAngle::kRadians), true);
                curve.setWeight(ixRight, cubic.weightRight(), true);
            }
        }
    }
    
    return MS::kSuccess;
}

MSyntax ReduceCommand::newSyntax() {
    MSyntax syntax;
    syntax.addFlag(kSelectionFlagShort, kSelectionFlagLong, MSyntax::kLong);
    syntax.makeFlagMultiUse(kSelectionFlagShort);
    syntax.setObjectType(MSyntax::kSelectionList, 0, 255);
    syntax.useSelectionAsDefault(false);
    return syntax;
}

MStatus ReduceCommand::GatherCommandArguments(const MArgList& args) {
    MStatus status;
    MArgDatabase argData(syntax(), args);
    
    if (argData.isFlagSet(kSelectionFlagShort)) {
        
        uint numUses = argData.numberOfFlagUses(kSelectionFlagShort);
        for (uint i = 0; i < numUses; i++) {
            MArgList argList;
            status = argData.getFlagArgumentList(kSelectionFlagShort, i, argList);
            if (!status) {
                std::ostringstream os; os << "Failed to read " << kSelectionFlagLong << " at index=" << i;
                Log::print(os.str());
                return status;
            }
            int s = argList.asInt(0, &status);
            selection.push_back(s);
        }
    }
    
    return MS::kSuccess;
}

