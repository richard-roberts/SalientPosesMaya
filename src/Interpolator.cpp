#include <sstream>

#include "common.hpp"
#include "AnimationProxy.hpp"
#include "Selector.hpp"
#include "Interpolator.hpp"

std::vector<HighDimCubic> Interpolate::optimal(const Eigen::MatrixXf& curve, std::vector<int> keyframes) {
	std::vector<HighDimCubic> ret = std::vector<HighDimCubic>();
    int start = keyframes[0];
	for (int i = 1; i < keyframes.size(); i++) {
		int from = keyframes.at(i - 1) - start;
		int to = keyframes.at(i) - start;
		HighDimCubic cubic = HighDimCubic::fitToCurve(curve, from, to);
		ret.push_back(cubic);
	}
	return ret;
}
