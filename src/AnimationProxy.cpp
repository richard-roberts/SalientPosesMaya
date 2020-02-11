#include <iostream>
#include <sstream>

#include "common.hpp"
#include "AnimationProxy.hpp"

AnimationProxy::AnimationProxy(Eigen::MatrixXf data): data(data) {
}

Eigen::VectorXf AnimationProxy::poseByIndex(int i) {
	Eigen::VectorXf p(getNDims());
    for (int d = 0; d < getNDims(); d++) {
		p[d] = data(d, i); 
    }
    return p;
}

Eigen::MatrixXf AnimationProxy::curveByIndex(int index) {
	Eigen::MatrixXf c(2, getNFrames());
	for (int f = 0; f < getNFrames(); f++) {
		c(0, f) = f;
		c(1, f) = data(index, f);
	}
	return c;
}

int AnimationProxy::save(std::string path) {
    std::ostringstream os;

	// Make the header
	os << "Frame";
    for (int i = 1; i < getNDims(); i++) {
        os << "," << "Dimension-" << i;
    }
    os << std::endl;
    
	// Make the body
    for (int i = 0; i < getNFrames(); i++) {
        Eigen::VectorXf p = poseByIndex(i);
		os << p[0];
        for (int i = 1; i < p.size(); i++) {
			os << "," << p[i];
        }
        os << std::endl;
    }
    
    std::cout << "  Saving animation to " << path << std::endl;
    return File::writeStringToFile(path, os.str());
}

AnimationProxy AnimationProxy::subAnimation(int fromIx, int toIx) {

	int nFrames = toIx - fromIx + 1;
	int nDims = data.rows();

	Eigen::MatrixXf subData(nDims, nFrames);
	for (int f = 0; f < nFrames; f++) {
		int ix = fromIx + f;

		for (int d = 0; d < nDims; d++) {	
			float v = data(d, ix);
			subData(d, f) = v;
		}
	}

	return AnimationProxy(subData);
}

AnimationProxy AnimationProxy::fromCSV(std::string path) {
	File file(path);
	std::vector< std::vector<std::string> > lines = file.divideByLineAndDelimiter(",");
	file.close();

	int nF = static_cast<int>(lines.size() - 1); // don't include the header
	int nD = static_cast<int>(lines[0].size());
	Eigen::MatrixXf data(nD, nF);

	int f = 0;
	for (int i = 1; i < lines.size(); i++) {
		std::vector<std::string> line = lines.at(i);

		for (int d = 0; d < line.size(); d++) {
			float v = static_cast<float>(atof(line.at(d).c_str()));
			data(d, f) = v;
		}

		f += 1;
	}

	return AnimationProxy(data);
}


