#pragma once

#include <math.h>

#include <stdio.h>
#include <iostream>
#include <string>
#include <vector>

#include "AnimationProxy.hpp"

#include "../eigen-git-mirror/Eigen/Dense"


class ErrorTable {
public:
	ErrorTable() { }
	static ErrorTable usingLineBasedError(AnimationProxy);
	static ErrorTable usingCurveBasedError(AnimationProxy);
	
	float errorIndex(int i, int j) const { return errorIndices(i, j); }
    float errorValue(int i, int j) const { return errorValues(i, j); }
    int save(std::string path);
 	
private:
	std::pair<int, float> indexAndErrorViaMaxPerpDistToLine(int, int);
	std::pair<int, float> indexAndErrorViaSumSqauredDistToCurve(int, int);
	
	ErrorTable(AnimationProxy anim) : anim(anim) {
		errorIndices = Eigen::MatrixXf(anim.getNFrames(), anim.getNFrames());
		errorValues = Eigen::MatrixXf(anim.getNFrames(), anim.getNFrames());
	}

	AnimationProxy anim;
	Eigen::MatrixXf errorIndices; 
	Eigen::MatrixXf errorValues;
    
};
