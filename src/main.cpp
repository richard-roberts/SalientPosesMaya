#include <iostream>
#include <string>
#include <sstream>
#include <algorithm>
#include <iterator>
#include <chrono> 

#include "common.hpp"
#include "AnimationProxy.hpp"
#include "ErrorTable.hpp"
#include "Selector.hpp"
#include "SelectionManager.hpp"
#include "Interpolator.hpp"

std::vector<int> parseCSVString(std::string s) {
	std::string delim = ",";
	std::vector<int> parts;
	size_t pos = 0;
	std::string token;
	while ((pos = s.find(delim)) != std::string::npos) {
		token = s.substr(0, pos);
		parts.push_back(std::stoi(token));
		s.erase(0, pos + delim.length());
	}
	parts.push_back(std::stoi(s));
	return parts;
}

int main (int argc, const char * argv[]) {    

	if (argc != 5) {
		std::cerr << "----------------------------------" << std::endl;
		std::cerr << "Invalid arguments" << std::endl;
		std::cerr << "-----------------" << std::endl;
		std::cerr << "You must provide 4 args:" << std::endl;
		std::cerr << "    1. filepath (string)" << std::endl;
		std::cerr << "    2. error type (string, can be `line` or `curve`)" << std::endl;
		std::cerr << "    3. n keyframes (int)" << std::endl;
		std::cerr << "    4. fixed keyframes (csv string, e.g. `12,30`, or use `x` for nothing)" << std::endl;
		std::cerr << "----------------------------------" << std::endl;
		return 1;
	}
	
	int argIx = 1;
	std::string filepath = argv[argIx++];
	std::string errorType = argv[argIx++];
	int nKeyframes = std::stoi(argv[argIx++]);
	std::string fixedKeyframesStr = argv[argIx++];
	std::vector<int> fixedKeyframes;
	if (strcmp(fixedKeyframesStr.c_str(), "x") != 0) {
		fixedKeyframes = parseCSVString(fixedKeyframesStr);
		std::sort(fixedKeyframes.begin(), fixedKeyframes.end());
	}

	std::cout << "----------------------------------" << std::endl;
	std::cout << "Running on " << filepath << std::endl;
	std::cout << "    using " << errorType << " based error function" << std::endl;
	std::cout << "    find up to " << nKeyframes << " keyframes" << std::endl;
	if (fixedKeyframes.size() == 0) {
		std::cout << "    with no keyframes fixed" << std::endl;
	} else {
		std::cout << "    with [" << fixedKeyframes[0];
		for (int i = 1; i < fixedKeyframes.size(); i++) { std::cout << ", " << fixedKeyframes[i]; }
		std::cout << "] as fixed keyframes" << std::endl;
	}
	std::cout << "----------------------------------" << std::endl;

	
	AnimationProxy anim = AnimationProxy::fromCSV(filepath);
	std::cout << "----------------------------------" << std::endl;
	std::cout << "The animation has " << anim.getNFrames() << " frames and " << anim.getNDims() << " dimensions" << std::endl;
	std::cout << "----------------------------------" << std::endl;

	std::cout << "----------------------------------" << std::endl;
	std::cout << "Starting selection:" << std::endl;

	std::cout << "    initializing manager... ";
	auto start = std::chrono::high_resolution_clock::now();
	SelectionManager manager(errorType, anim, fixedKeyframes);
	auto end = std::chrono::high_resolution_clock::now();
	double micros = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
	std::cout << " took " << micros << "ms" << std::endl;

	std::cout << "    doing selection... ";
	start = std::chrono::high_resolution_clock::now();
	manager.incrementUntilNKeyframes(nKeyframes);
	end = std::chrono::high_resolution_clock::now();
	micros = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
	std::cout << " took " << micros << "ms" << std::endl;
	
	SelectionProxy proxy = manager.getFinalSelectionProxy();
	std::cout << "Final selections:" << std::endl;

	for (int i = proxy.getMinKeyframes(); i < proxy.getMaxKeyframes(); i++) {
		std::vector<int> keyframes = proxy.getSelectionByNKeyframes(i);
		std::cout << "    " << keyframes.size() << ": [" << keyframes[0];
		for (int i = 1; i < keyframes.size(); i++) {
			std::cout << ", " << keyframes[i];
		}
		std::cout << "]" << std::endl;
	}
	std::cout << "----------------------------------" << std::endl;


	std::cout << "----------------------------------" << std::endl;
	std::cout << "Starting interpolation:" << std::endl;
	std::vector<int> keyframes = proxy.getSelectionByNKeyframes(nKeyframes);
	int curveIx = 1;
	Eigen::MatrixXf curve = anim.curveByIndex(curveIx);
	std::vector<HighDimCubic> cubics = Interpolate::optimal(curve, keyframes);

	std::ostringstream os2;
	os2 << "Fitting: " << std::endl;
	for (int i = 0; i < cubics.size(); i++) {
		os2 << "----- SEGMENT " << (i + 1) << " -----------------" << std::endl;
		os2 << "    P1: " << cubics[i].p1.transpose() << std::endl;
		os2 << "    P2: " << cubics[i].p2.transpose() << std::endl;
		os2 << "    P3: " << cubics[i].p3.transpose() << std::endl;
		os2 << "    P4: " << cubics[i].p4.transpose() << std::endl;
	}
	std::cout << "----------------------------------" << std::endl;

	
	std::cout << os2.str() << std::endl;

    return 0;
}
