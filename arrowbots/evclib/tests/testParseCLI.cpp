// Compile with
// g++ -std=c++11 -Wall -o testParseCLI testParseCLI.cpp parseCLI.cpp

#include <iostream>
#include <tuple>

#include "../parseCLI.h"

int main(int argc, char** argv)
{
	std::string inFN, outFN;
	std::tie(inFN, outFN) = parsecli::twoFilenamesForIO(argc, argv, "testParseCLI");
	std::cout << "Got filenames " << inFN << " and " << outFN << std::endl;
	return 0;
}
