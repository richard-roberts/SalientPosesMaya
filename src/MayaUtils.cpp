//
//  MayaUtils.cpp
//  SalientPosesMaya
//
//  Created by Richard Roberts on 3/04/18.
//

#include <sstream>
#include <stdexcept>

#include <maya/MGlobal.h>

#include "MayaUtils.hpp"

/* Logging
 *
 * 0 - Maya global output only
 * 1 - Maya global output and standard output
 */
#define LOGGING 0

std::string mStringForErrorType(MStatus status) {
    if (status == MS::kSuccess) {
        return "Success";
    } else if (status == MS::kFailure) {
        return "Generic";
    } else if (status == MS::kInsufficientMemory) {
        return "InsufficientMemory";
    } else if (status == MS::kInvalidParameter) {
        return "InvalidParameter";
    } else if (status == MS::kLicenseFailure) {
        return "LicenseFailure";
    } else if (status == MS::kUnknownParameter) {
        return "UnknownParameter";
    } else if (status == MS::kNotImplemented) {
        return "NotImplemented";
    } else if (status == MS::kNotFound) {
        return "NotFound";
    } else if (status == MS::kEndOfFile) {
        return "endOfFile";
    } else {
        std::ostringstream os;
        os << status.statusCode();
        throw std::runtime_error("Status not understood (code=" + os.str() + ")");
    }
}

void Log::print(MString message) {
    if (LOGGING==1) std::cout << message << std::endl;
    MGlobal::displayInfo(message);
}

void Log::warning(MString message) {
    if (LOGGING == 1) std::cout << "WARNING: " << message << std::endl;
    MGlobal::displayWarning(message);
}

void Log::error(MString message) {
    if (LOGGING == 1) std::cerr << "ERROR: " << message << std::endl;
    MGlobal::displayError(message);
}

void Log::showStatus(MStatus status, std::string message) {
    std::string messageStr = message;
    
    if (status == MS::kSuccess) {
        print(MString(("Success: " + messageStr).c_str()));
        return;
    }
    
    std::string errorPart = status.errorString().asChar();
    std::string suffix = "[" + errorPart + "]";
    std::string errorString = mStringForErrorType(status) + ": " + messageStr + " " + suffix;
    error(MString(errorString.c_str()));
}

void Log::showStatus(MStatus status) {
    if (status == MS::kSuccess) {
        print(MString("Success"));
        return;
    }
    std::string errorString = mStringForErrorType(status) + status.errorString().asChar();
    error(MString(errorString.c_str()));
}

void Log::showStatusWhenError(MStatus status, std::string message) {
    if (status == MS::kSuccess) { return; }
    showStatus(status, message);
}

void Log::showStatusWhenError(MStatus status) {
    if (status == MS::kSuccess) { return; }
    showStatus(status);
}

void MayaCheck::objectIsPointArray(MObject obj) {
    MFn::Type type = obj.apiType();
    if (type != MFn::kPointArrayData) {
        std::ostringstream os; os << "Element was not of type MPointArray";
        throw std::runtime_error(os.str());
    }
}

void MayaCheck::objectIsFloatArray(MObject obj) {
    MFn::Type type = obj.apiType();
    if (type != MFn::kFloatArrayData) {
        std::ostringstream os; os << "Element was not of type MFloatArray";
        throw std::runtime_error(os.str());
    }
}

MTime::Unit MayaConfig::getCurrentFPS() {
    return MTime::uiUnit();
}


MAngle::Unit MayaConfig::getCurrentAngleUnit() {
    return MAngle::uiUnit();
}

