#include <stdio.h>
#include <iostream>
#include <fstream>

#include "common.hpp"

#define VERBOSE 0

#define FITTING_ITERATIONS 4
#define SAMPLES_PER_CURVE 10
#define FITTING_RESOLUTION 100

HighDimCubic HighDimCubic::fitToCurve(const Curve& curve, int from, int to) {

	std::vector<float> samples;
	float denom = SAMPLES_PER_CURVE - 1;
	for (int i = 0; i < SAMPLES_PER_CURVE; i++) {
		samples.push_back(i / denom);
	}

	int nDims = curve.data.rows();

	Eigen::Matrix<float, SAMPLES_PER_CURVE, 2> R14;
	Eigen::Matrix<float, SAMPLES_PER_CURVE, 2> R23;
	Eigen::Matrix<float, 1, 4> r;
	Eigen::Matrix<float, 1, 4> rm;
	
	Eigen::Matrix4f M;
	M(0, 0) = -1.0; M(0, 1) = 3.0; M(0, 2) = -3.0; M(0, 3) = 1.0;
	M(1, 0) = 3.0; M(1, 1) = -6.0; M(1, 2) = 3.0; M(1, 3) = 0.0;
	M(2, 0) = -3.0; M(2, 1) = 3.0; M(2, 2) = 0.0; M(2, 3) = 0.0;
	M(3, 0) = 1.0; M(3, 1) = 0.0; M(3, 2) = 0.0; M(3, 3) = 0.0;

	Eigen::VectorXf p1;
	Eigen::VectorXf p2;
	Eigen::VectorXf p3;
	Eigen::VectorXf p4;

	Eigen::MatrixXf A = Eigen::MatrixXf(SAMPLES_PER_CURVE, nDims);
	Eigen::MatrixXf C14 = Eigen::MatrixXf(2, nDims);
	Eigen::MatrixXf C23 = Eigen::MatrixXf(2, nDims);
	Eigen::MatrixXf b;
	Eigen::VectorXf p;
	Eigen::VectorXf interp;

	for (int i = 0; i < FITTING_ITERATIONS; i++) {
		for (int j = 0; j < SAMPLES_PER_CURVE; j++) {

			float u = samples[j];

			// Set sampling parameter into row
			r(0, 0) = pow(u, 3);
			r(0, 1) = pow(u, 2);
			r(0, 2) = u;
			r(0, 3) = 1;

			// Dot row with coeffecient matrix
			rm = r * M;

			// Set matrix R using (sampling . coeffecient)
			R14(j, 0) = rm(0, 0);
			R23(j, 0) = rm(0, 1);
			R23(j, 1) = rm(0, 2);
			R14(j, 1) = rm(0, 3);

			// Set curve data into matrix A
			float x = from + (to - from) * u;
			curve.sampleAt(interp, x);
			A.row(j) = interp;

			// Set C14 (only first and last frame)
			if (j == 0) { 
				C14.row(0) = A.row(j);
			} else if (j == SAMPLES_PER_CURVE - 1) {
				C14.row(1) = A.row(j);
			}
		}

		// Create b
		b = A - R14 * C14;

		// Solve linear system
		C23 = R23.colPivHouseholderQr().solve(b);
		p1 = C14.row(0);
		p2 = C23.row(0);
		p3 = C23.row(1);
		p4 = C14.row(1);

		for (int j = 0; j < SAMPLES_PER_CURVE; j++) {
			float x = from + (to - from) * (j / denom);
			float best_u = -1;
			float min_dist = 999.0f;
			for (int k = 0; k < FITTING_RESOLUTION; k++) {
				float u = k / float(FITTING_RESOLUTION - 1);
				float oneSubU = 1 - u;
				float p1c = pow(oneSubU, 3);
				float p2c = 3 * pow(oneSubU, 2) * u;
				float p3c = 3 * oneSubU * pow(u, 2);
				float p4c = pow(u, 3);
				p = p1 * p1c;
				p += p2 * p2c;
				p += p3 * p3c;
				p += p4 * p4c;
				curve.sampleAt(interp, x);
				float dist = (p - interp).norm();
				if (dist < min_dist) {
					min_dist = dist;
					best_u = u;
				}
			}

			samples[j] = best_u;
		}
	}

	// Extract solved "control points" and use them to make a new cubic
	return HighDimCubic(C14.row(0), C23.row(0), C23.row(1), C14.row(1));
}

std::vector<std::string> divideLineIntoParts(char line[], const char* delimiter) {
    const char* tok;
    std::vector<std::string> parts;
    for (tok = strtok(line, delimiter); tok && *tok; tok = strtok(NULL, ",\n")) {
        parts.push_back(tok);
    }
    return parts;
}

File::File(std::string path) {
    this->path = path;
	if (VERBOSE > 0) {
		std::cout << "Loading file: " << path << std::endl;
	}
    file = fopen(path.c_str(), "r");
}

std::vector< std::vector<std::string> > File::divideByLineAndDelimiter(std::string delimiter) {
    char line[32768];
    const char* delim = delimiter.c_str();
    
    std::vector< std::vector<std::string> > output;
    while (fgets(line, 32768, file)) {
        std::vector<std::string> parts = divideLineIntoParts(line, delim);
        output.push_back(parts);
    }
    return output;
}

int File::writeStringToFile(std::string filepath, std::string content) {
    std::ofstream handle;
    handle.open(filepath);
    handle << content;
    handle.close();
    return 0;
}

std::string File::getDirectory() {
    size_t found;
    found = path.find_last_of("/\\");
    return path.substr(0, found);
}

void File::close() {
    fclose(file);
}

bool OS::doesFileExist(std::string path) {
    std::ifstream infile(path);
	return infile.good();
}
