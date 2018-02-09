/* Compile with
	bulletPath=../bullet3-2.82; g++ -std=c++11 -I${bulletPath}/src -I${bulletPath}/Demos/OpenGL -o a.out ANNHiddenRecursive.cpp testANNHiddenRecursive.cpp ../misc.cpp
*/

#include <iostream>
#include <vector>

// TODO: broken

//#include "ANNHiddenRecursive.h"
//#include "../misc.h"

void testRecurrentNetwork(NeuralNetwork& nn1, const Percept& testInput)
{
	nn1.print();
	for(int i=0; i<10; i++)
	{
		auto testOutput = nn1.output(testInput);
		std::cout << "Input: " << str(testInput);
		std::cout << " Output: " << str(testOutput) << " Hidden: ";
		nn1.printHidden();
	}
	std::cout << std::endl;
};

int main(int argc, char** argv)
{
	NeuralNetwork nn0("42 1 0 0 1 0.5 0 0 0.5 0 0 0 0 1 0 0 1");
	nn0.print();
	std::vector<Percept> testInputs{{1,0,0,0}, {0,1,0,0}, {0,0,1,0}, {0,0,0,1}, {1,1,-1,1}};
	for(auto testInput : testInputs)
	{
		auto testOutput = nn0.output(testInput);
		nn0.resetHidden();
		std::cout << "Input: " << str(testInput);
		std::cout << " Output: " << str(testOutput);
		std::cout << std::endl;
	}
	std::cout << std::endl;

	NeuralNetwork nn1("43 1 0 0 1 0.5 0 0 0.5 1 0 0 1 1 0 0 1");
	testRecurrentNetwork(nn1, testInputs[0]);
	NeuralNetwork nn2("44 -1 0 0 1 0.5 0 0 0.5 -1 1 1 0 1 0 0 1");
	testRecurrentNetwork(nn2, testInputs[0]);

	std::vector<ANNNodeStateType> compVals{1.5, 1.0, 0.5, 0.0, -0.5};
	std::cout << "Comparison values: " << std::endl;
	for(auto val : compVals)
		std::cout << " sigmoid(sigmoid(" << val << ")) = " << sigmoid(sigmoid(val)) << std::endl;

	std::cout << " sigmoid(0.8660+1) is " << sigmoid(1.8660) << std::endl;
	return 0;
}
