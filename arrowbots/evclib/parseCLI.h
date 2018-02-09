#ifndef EVCLIB_PARSE_CLI_H
#define EVCLIB_PARSE_CLI_H

#include <string>
#include <tuple>
#include <iostream>
#include <cstdlib>

namespace parsecli
{
	std::pair<std::string, std::string> twoFilenamesForIO(int argc, char** argv, std::string appName = "client")
	{
		if(argc == 3)
			return std::make_pair(std::string(argv[1]), std::string(argv[2]));

		std::cout << "Usage: " << appName << " <pathToInputFile> <pathToOutputFile>\n";
		exit(EXIT_FAILURE);
	};
}

#endif // EVCLIB_PARSE_CLI_H
