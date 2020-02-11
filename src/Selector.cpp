//
//  Selector.cpp
//  SalientPosesPerformance
//
//  Created by Richard Roberts on 04/02/18.
//

#include <stdio.h>
#include <iostream>
#include <sstream>
#include <limits.h>
#include <algorithm>

#include "common.hpp"
#include "Selector.hpp"


float errorForSelection(const ErrorTable& table, std::vector<int> sel) {
	float maxError = 0;
	for (int i = 1; i < sel.size(); i++) {
		float e = table.errorValue(sel[i - 1], sel[i]);
		if (e > maxError) {
			maxError = e;
		}
	}
	return maxError;
}

SelectionRow::SelectionRow(int nFrames, const ErrorTable& table) :
	nFrames(nFrames), table(table) {
        
    for (int j = 1; j < nFrames; j++) {
		errors[j] = table.errorValue(0, j);
        std::vector<int> sel(2, -1);
        sel[0] = 0;
        sel[1] = j;
        selections[j] = sel;
    }
}

Selector::Selector(const AnimationProxy anim, const ErrorTable errorTable) :
	anim(anim), table(errorTable) {

	int nFrames = anim.getNFrames();

	// Make the first guy
	std::vector<int> firstSelection;
	firstSelection.push_back(0);
	firstSelection.push_back(nFrames - 1);
	float firstError = errorTable.errorValue(0, nFrames - 1);
	rows.push_back(SelectionRow(nFrames, errorTable));
	nKeyframes = 2;
	selections[2] = firstSelection;
	errors[2] = firstError;
	lastSelection = firstSelection;
	lastError = firstError;
	
}

void Selector::next() {

	nKeyframes = nKeyframes + 1;

	int nFrames = anim.getNFrames();

	SelectionRow previous = rows.at(rows.size() - 1);
	SelectionRow next = SelectionRow(nFrames, table);

	int kOptimal;
	float bestValue, value, akValue, keValue;

	for (int e = nKeyframes - 1; e < nFrames; ++e) {
		kOptimal = -1;
		bestValue = std::numeric_limits<float>::infinity();

		for (int k = nKeyframes - 2; k < e; ++k) {

			// Get current value
			akValue = previous.getErrorValue(k);
			keValue = table.errorValue(k, e);

			if (akValue > keValue) {
				value = akValue;
			}
			else {
				value = keValue;
			}

			// Update optimal when current value is less than min value
			if (value < bestValue) {
				bestValue = value;
				kOptimal = k;
			}
		}

		// Update values and selections in next table
		std::vector<int> next_sel = previous.getSelection(kOptimal);
		next_sel.push_back(e);
		next.setErrorValue(e, bestValue);
		next.setSelection(e, next_sel);
	}

	rows.push_back(next);
	SelectionRow lastRow = rows.at(rows.size() - 1);
	std::vector<int> finalSelection = lastRow.getSelection(nFrames - 1);
	float finalError = errorForSelection(table, finalSelection);

	int n = finalSelection.size();
	selections[n] = finalSelection;
	errors[n] = finalError;
	lastSelection = finalSelection;
	lastError = finalError;
}
