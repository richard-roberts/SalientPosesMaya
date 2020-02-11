#pragma once

#include <stdio.h>
#include <string>
#include <vector>

#include "../eigen-git-mirror/Eigen/Dense"


class AnimationProxy {
    
public:
	AnimationProxy() {};
	AnimationProxy(Eigen::MatrixXf);
	int getNFrames() const { return data.cols(); }
	int getNDims() { return data.rows(); }
	Eigen::MatrixXf curveByIndex(int); 
	Eigen::VectorXf poseByIndex(int);
	int save(std::string);
	AnimationProxy subAnimation(int fromIx, int toIx);
	static AnimationProxy fromCSV(std::string);
    
	Eigen::MatrixXf data;
};
