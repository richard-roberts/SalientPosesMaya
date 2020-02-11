#include <iostream>
#include <sstream>
#include <limits.h>

#include "../eigen-git-mirror/Eigen/Dense"

#include "AnimationProxy.hpp"
#include "ErrorTable.hpp"
#include "common.hpp"

ErrorTable ErrorTable::usingLineBasedError(AnimationProxy anim) {
	ErrorTable table = ErrorTable(anim);

	#pragma omp parallel for collapse(2)
	for (int i = 0; i < anim.getNFrames(); i++) {
		for (int j = i + 1; j < anim.getNFrames(); j++) {
			std::pair<int, float> indexAndValue = table.indexAndErrorViaMaxPerpDistToLine(i, j);
			table.errorIndices(i, j) = indexAndValue.first;
			table.errorValues(i, j) = indexAndValue.second;
		}
	}

	return table;
}

ErrorTable ErrorTable::usingCurveBasedError(AnimationProxy anim) {
	ErrorTable table = ErrorTable(anim);

	#pragma omp parallel for collapse(2)
	for (int i = 0; i < anim.getNFrames(); i++) {
		for (int j = i + 1; j < anim.getNFrames(); j++) {
			int nFrames = j - i + 1;
			if (nFrames == 2) {
				table.errorIndices(i, j) = i;
				table.errorValues(i, j) = 0.0;
			} else if (nFrames == 3) {
				table.errorIndices(i, j) = i+1;
				table.errorValues(i, j) = 0.0;
			} else if (nFrames == 4) {
				table.errorIndices(i, j) = i + 1;
				table.errorValues(i, j) = 0.0;
			} else {
				std::pair<int, float> indexAndValue = table.indexAndErrorViaSumSqauredDistToCurve(i, j);
				table.errorIndices(i, j) = indexAndValue.first;
				table.errorValues(i, j) = indexAndValue.second;
			}
			
		}
	}

	return table;
}

int ErrorTable::save(std::string path) {
	std::string content = "i,j,errorIndex,errorValue\n";

	for (int i = 0; i < errorIndices.rows(); i++) {
		for (int j = i + 1; j < errorIndices.cols(); j++) {
			std::ostringstream os;
			os << i << "," << j << ",";
			os << errorIndex(i, j) << ",";
			os << errorValue(i, j) << std::endl;
			content += os.str();
		}
	}

	std::cout << "  Saving error table to " << path << std::endl;
	return File::writeStringToFile(path, content);
}	

std::pair<int, float> ErrorTable::indexAndErrorViaMaxPerpDistToLine(int i, int j) {
	Eigen::VectorXf a = anim.poseByIndex(i);
	Eigen::VectorXf b = anim.poseByIndex(j);
	float distEnd2End = (a - b).norm();
	Eigen::VectorXf vnEnd2End = (a - b) / distEnd2End;

	float maxDist = 0.0f;
	int maxIndex = -1;
	for (int k = i + 1; k < j; k++) {
		Eigen::VectorXf c = anim.poseByIndex(k);
		float dot = (c - a).dot(vnEnd2End);
		Eigen::VectorXf p = a + dot * vnEnd2End;
		float dist = (p - c).norm();
		if (dist > maxDist) {
			maxDist = dist;
			maxIndex = k;
		}
	}
    
	std::pair<int, float> ret;
	ret.first = maxIndex;
	ret.second = maxDist;
	return ret;
}

std::pair<int, float> ErrorTable::indexAndErrorViaSumSqauredDistToCurve(int i, int j) {
	Curve curve(anim.data);
	HighDimCubic cubic = HighDimCubic::fitToCurve(curve, i, j);	

	int nDims = anim.data.rows();
	
	Eigen::MatrixXf r(1, 4);
	Eigen::MatrixXf rm(1, 4);

	Eigen::VectorXf a;
	Eigen::VectorXf b;

	int nSamples = 10;
	float sumSquaredDist = 0.0f;
	float maxDist = 0.0f;
	int maxIndex = -1;
	for (int s = 0; s < nSamples; s++) {
		float u = s / (nSamples - 1.0);
		a = cubic.sampleAt(u);
		float x = i + (j - i) * u;
		curve.sampleAt(b, x);
		float dist = (a - b).norm();
		sumSquaredDist += dist * dist;
		if (dist > maxDist) {
			maxDist = dist;
			maxIndex = (int) round(x);
		}
	}
	
	std::pair<int, float> ret;
	ret.first = maxIndex;
	ret.second = sumSquaredDist;
	return ret;
}
