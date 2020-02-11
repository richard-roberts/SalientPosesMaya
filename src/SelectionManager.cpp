//
//  SelectionManager.cpp
//  SalientPosesPerformance
//
//  Created by Richard Roberts on 25/09/18.
//

#include "ErrorTable.hpp"
#include "Selector.hpp"
#include "SelectionManager.hpp"

SelectionManager::SelectionManager(std::string errorType, AnimationProxy anim, std::vector<int> fixedKeyframes) {
	
	if (fixedKeyframes.size() == 0) {
		fixedKeyframes.insert(fixedKeyframes.begin(), 0);
		fixedKeyframes.push_back(anim.getNFrames() - 1);
	} else {
		if (fixedKeyframes[0] != 0) {
			fixedKeyframes.insert(fixedKeyframes.begin(), 0);
		}
		if (fixedKeyframes[fixedKeyframes.size() - 1] != anim.getNFrames() - 1) {
			fixedKeyframes.push_back(anim.getNFrames() - 1);
		}
	}

	for (int i = 1; i < fixedKeyframes.size(); i++) {
		int s = fixedKeyframes[i - 1];
		int e = fixedKeyframes[i];
		segmentStartFrames.push_back(s); 
		keyframesToUseInEachSegment.push_back(2); 
		AnimationProxy subAnim = anim.subAnimation(s, e);
		ErrorTable table;
		if (errorType == "line") {
			table = ErrorTable::usingLineBasedError(subAnim);
		} else if (errorType == "curve") {
			table = ErrorTable::usingCurveBasedError(subAnim);
		} else {
			std::cerr << "Invalid error type, this should not happen (as this arguments is parsed by main)" << std::endl;
		}
		selectors.push_back(Selector(subAnim, table));
	}

	std::vector<int> selection = getCombinedSelection();
	float error = getMaxErrorAcrossSegments();
	int n = selection.size();
	finalSelections[n] = selection;
	finalErrors[n] = error;
}

void SelectionManager::incrementUntilNKeyframes(int nKeyframes) {

	int n = getCombinedSelection().size();

    while (n <= nKeyframes) {
        
		float maxErrorReduce = 0.0f;
		int maxErrorReduceIx = -1;

		for (int i = 0; i < selectors.size(); i++) {
			int nKeyframesCurrent = keyframesToUseInEachSegment[i];
			if (nKeyframesCurrent == selectors[i].maximumKeyframes()) {
				continue;
			}
			selectors[i].next();
			float errorNow = selectors[i].getErrorByNKeyframes(nKeyframesCurrent);
			float errorNext = selectors[i].getErrorByNKeyframes(nKeyframesCurrent + 1);
			float errorReduce = errorNow - errorNext;

			// Keep the highest reduction
			if (errorReduce >= maxErrorReduce) {
				maxErrorReduce = errorReduce;
				maxErrorReduceIx = i;
			}
		}

		if (maxErrorReduceIx == -1) {
			std::cerr << "No reduction in error found at all - why did this happen?" << std::endl;
		}

		keyframesToUseInEachSegment[maxErrorReduceIx] = keyframesToUseInEachSegment[maxErrorReduceIx] + 1;

		std::vector<int> selection = getCombinedSelection();
		float error = getMaxErrorAcrossSegments();
		int n2 = selection.size();
		finalSelections[n2] = selection;
		finalErrors[n2] = error;
		
		n += 1;
    }
}

float SelectionManager::getMaxErrorAcrossSegments() {
    float errorMaxTotal = 0;
    
    int n = selectors.size();
    for (int i = 0; i < n; i++) {
		int nKeyframes = keyframesToUseInEachSegment[i];
        float errorForSegment = selectors[i].getErrorByNKeyframes(nKeyframes);
        if (errorForSegment > errorMaxTotal) {
            errorMaxTotal = errorForSegment;
        }
    }
    
    return errorMaxTotal;
}

std::vector<int> SelectionManager::getCombinedSelection() {

	std::vector<int> ret;

	// Copy in selection from each segement
	int n = selectors.size();
	for (int i = 0; i < n; i++) {
		int s = segmentStartFrames[i];

		int nKeyframes = keyframesToUseInEachSegment[i];
		std::vector<int> selForSegment = selectors[i].getSelectionByNKeyframes(nKeyframes);

		if (i < n - 1) {
			// Skip the last keyframe, as it's duplicated by the next segment's first keyframe
			for (int j = 0; j < selForSegment.size() - 1; j++) {
				ret.push_back(s + selForSegment[j]);
			}
		} else {
			// Copy in all keyframes, as there is no next segment
			for (int j = 0; j < selForSegment.size(); j++) {
				ret.push_back(s + selForSegment[j]);
			}
		}
	}

	return ret;
}
