#pragma once

#include <map>

#include "ErrorTable.hpp"
#include "SelectionProxy.hpp"


class SelectionRow {
public:
    SelectionRow(int nFrames, const ErrorTable& errorTable);
    float getErrorValue(int e) { return errors[e]; }
    void setErrorValue(int e, float value) { errors[e] = value; }
    std::vector<int> getSelection(int e) { return selections[e]; }
    void setSelection(int e, std::vector<int> selection) {  selections[e] = selection; }
private:
    int nFrames;
    const ErrorTable& table;
    std::map< int, float > errors;
    std::map< int, std::vector<int> > selections;
};

class Selector {
public:
	Selector(const AnimationProxy anim, const ErrorTable errorTable);
	void next();
	SelectionProxy getProxy() { return SelectionProxy(selections, errors); }
	void upToN(int maxKeyframes) { while (nKeyframes <= maxKeyframes) { next(); nKeyframes += 1; } }
	int countKeyframes() { return nKeyframes; }
	std::vector<int> getLastSelection() { return lastSelection; }
	int getLastError() { return lastError; }
	float getErrorByNKeyframes(int n) { return errors[n]; }
	std::vector<int> getSelectionByNKeyframes(int n) { return selections[n]; }
	int maximumKeyframes() { return anim.getNFrames(); }
private:
	AnimationProxy anim;
	ErrorTable table;
	std::vector<SelectionRow> rows;
	std::map< int, std::vector<int> > selections;
	std::map< int, float > errors;
	int nKeyframes;	
	std::vector<int> lastSelection;
	float lastError;
};
