#pragma once

#include <map>

#include "AnimationProxy.hpp"
#include "SelectionProxy.hpp"

class SelectionManager {
    
public:
	SelectionManager(std::string errorType, AnimationProxy, std::vector<int> fixedKeyframes);
    void incrementUntilNKeyframes(int);
    float getMaxErrorAcrossSegments();
    std::vector<int> getCombinedSelection();
	SelectionProxy getFinalSelectionProxy() { return SelectionProxy(finalSelections, finalErrors); }
    
private:
	int maxKeyframes;
	std::vector<int> segmentStartFrames;
	std::vector<int> keyframesToUseInEachSegment;
    std::vector<Selector> selectors;
	std::map< int, std::vector<int> > finalSelections;
	std::map< int, float > finalErrors;
};
