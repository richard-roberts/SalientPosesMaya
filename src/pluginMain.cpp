#include <sstream>

#include <maya/MFnPlugin.h>
#include <maya/MGlobal.h>
#include <maya/MIOStream.h>
#include <maya/MString.h>
#include <maya/MStatus.h>

#include "SelectCommand.hpp"
#include "ReduceCommand.hpp"
#include "MayaUtils.hpp"

MStatus initializePlugin(MObject obj) {
    MStatus status;
    MFnPlugin plugin(obj, "Richard Roberts", "0.2.0", "201810");
    
	status = plugin.registerCommand(SelectCommand::kName, SelectCommand::creator);
    if (status != MS::kSuccess) { Log::error(std::string(SelectCommand::kName) + " failed to register"); }

    status = plugin.registerCommand(ReduceCommand::kName, ReduceCommand::creator);
    if (status != MS::kSuccess) { Log::error(std::string(ReduceCommand::kName) + " failed to register"); }
    
    return status;
}

MStatus uninitializePlugin(MObject obj) {
    MStatus status;
    MFnPlugin plugin(obj);
    
	status = plugin.deregisterCommand(SelectCommand::kName);
    if (status != MS::kSuccess) { Log::error(std::string(SelectCommand::kName) + " failed to deregister"); }

    status = plugin.deregisterCommand(ReduceCommand::kName);
    if (status != MS::kSuccess) { Log::error(std::string(ReduceCommand::kName) + " failed to deregister"); }
    
    return status;
}
