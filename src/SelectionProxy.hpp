#pragma once

#include <cmath>
#include <vector>
#include <stdio.h>
#include <iostream>
#include <iterator>
#include <map>

class SelectionProxy {
    
public:
	SelectionProxy() {}
	SelectionProxy(std::map< int, std::vector <int> > selections, std::map<int, float> errors);
	int nSelections() { return static_cast<int>(selections.size()); }
	float getErrorByNKeyframes(int n) { return errors[n]; }    
	std::vector<int> getSelectionByNKeyframes(int n) { return selections[n]; }

	int getMaxKeyframes() { 
		int maxN = 0;
		for (std::map<int, float>::iterator iter = errors.begin(); iter != errors.end(); ++iter) {
			int n = iter->first; if (n > maxN) { maxN = n; }
		}
		return maxN;
	}

	int getMinKeyframes() {
		int minN = 99999999;
		for (std::map<int, float>::iterator iter = errors.begin(); iter != errors.end(); ++iter) {
			int n = iter->first; if (n < minN) { minN = n; }
		}
		return minN;
	}

    int save(std::string path);
 
private:
    std::map< int, std::vector <int> > selections;
    std::map< int, float> errors;
};
