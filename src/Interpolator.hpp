#pragma once

#include <vector>
#include <math.h>

#include "../eigen-git-mirror/Eigen/Dense"

#include "AnimationProxy.hpp"
#include "SelectionProxy.hpp"
#include "common.hpp"

class Interpolate {
public:
	static std::vector<HighDimCubic> optimal(const Eigen::MatrixXf& curve, std::vector<int> keyframes);
};
