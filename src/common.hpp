#pragma once

#include <stdio.h>
#include <string>
#include <vector>
#include <string.h>

#include "../eigen-git-mirror/Eigen/Dense"

class Curve {

public:

	Curve(const Eigen::MatrixXf& data) : data(data) {}

	void sampleAt(Eigen::VectorXf& interp, float x) const {
		int left_ix = floor(x);
		int right_ix = ceil(x);
		if (left_ix == right_ix) {
			interp = data.col(left_ix);
		} else {
			float t = x - left_ix;
			interp = data.col(left_ix) + (data.col(right_ix) - data.col(left_ix)) * t;
		}
		
	}

	Eigen::MatrixXf data;

};

class HighDimCubic {

public:
	HighDimCubic() {}

	HighDimCubic(Eigen::VectorXf p1, Eigen::VectorXf p2, Eigen::VectorXf p3, Eigen::VectorXf p4) {
		this->p1 = p1; this->p2 = p2; this->p3 = p3; this->p4 = p4;
		this->nDims = p1.rows();
	}

	HighDimCubic(const HighDimCubic& other) {
		p1 = other.p1; p2 = other.p2; p3 = other.p3; p4 = other.p4;
		this->nDims = p1.rows();
	}

	Eigen::VectorXf sampleAt(float u) {
		float oneSubU = 1 - u;
		return
			p1 * (oneSubU * oneSubU * oneSubU) +
			p2 * 3 * (oneSubU * oneSubU) * u +
			p3 * 3 * oneSubU * (u * u) +
			p4 * (u * u * u);
	}

	static HighDimCubic fitToCurve(const Curve& curve, int from, int to);

	Eigen::VectorXf p1;
	Eigen::VectorXf p2;
	Eigen::VectorXf p3;
	Eigen::VectorXf p4;
	int nDims;

};

class File {
public:
    File(std::string path);
    std::vector< std::vector<std::string> > divideByLineAndDelimiter(std::string delimiter);
    void close();
    static int writeStringToFile(std::string filepath, std::string content);
    std::string getDirectory();
private:
    FILE *file;
    std::string path;
};

class OS {
public:
    static bool doesFileExist(std::string path);
};
