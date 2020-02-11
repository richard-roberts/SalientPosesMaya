//
//  SelectionProxy.cpp
//  SalientPosesPerformance
//
//  Created by Richard Roberts on 3/04/18.
//

#include <stdio.h>
#include <iostream>
#include <string>
#include <sstream>

#include "common.hpp"
#include "SelectionProxy.hpp"


#define VERBOSE 1

SelectionProxy::SelectionProxy(std::map< int, std::vector <int> > selections, std::map<int, float> errors) :
	selections(selections), errors(errors)
{
}

int SelectionProxy::save(std::string path) {
    std::string content = "";
    
    // Setup header
    std::ostringstream osHeader; osHeader << "n_keyframes,error";
    std::vector<int> lastSelection = selections.at(selections.size() - 1);
    for (int i = 0; i < lastSelection.size(); i++) {
        osHeader << "," << "k" << i + 1;
    }
    osHeader << std::endl;
    content += osHeader.str();
    
    // Add n keyframes, error, and selection
    for (int i = 0; i < selections.size(); i++) { // skip the first row
        std::vector<int> sel = selections.at(i);
        std::ostringstream os;
        os << sel.size() << "," << errors.at(i);
        for (int j = 0; j < sel.size(); j++) { os << "," << sel[j]; }
        os << std::endl;
        content += os.str();
    }
    
    if (VERBOSE > 0) {
		std::cout << " Saving selection table to " << path << std::endl;
    }
    return File::writeStringToFile(path, content);
}
