/* Compile with
	bulletPath=../bullet3-2.82; g++ -std=c++11 -I${bulletPath}/src -I${bulletPath}/Demos/OpenGL -o a.out ANNDirect.cpp testANNDirect.cpp ../misc.cpp
*/

#include <iostream>
#include <vector>

// TODO: broken

//#include "ANNDirect.h"
//#include "../misc.h"

int main(int argc, char** argv)
{
	NeuralNetwork nn0("42 1 0.5 -0.5 1 1 1 1 1");
	nn0.print();
	std::vector<Percept> testInputs{{1,0,0,0}, {0,1,0,0}, {0,0,1,0}, {0,0,0,1}, {1,1,-1,1}};
	for(auto testInput : testInputs)
	{
		auto testOutput = nn0.output(testInput);
		std::cout << "Input: ";
		for(auto elem : testInput)
			std::cout << elem << " ";
		std::cout << "Output: ";
		for(auto elem : testOutput)
			std::cout << elem << " ";
		std::cout << std::endl;
	}
	std::cout << std::endl;

	std::vector<ANNNodeStateType> compVals{1.5, 1.0, 0.5, -0.5};
	std::cout << "Comparison values: " << std::endl;
	for(auto val : compVals)
		std::cout << " sigmoid(" << val << ") = " << sigmoid(val) << std::endl;
	return 0;
}
