/* Compile with
	g++ -std=c++11 -o testDirect ../../ann/direct.cpp testDirect.cpp

	Correct output when used with logistic transfer function:

	Hyperparameters: input nodes: 4 output nodes: 2 transfer function at zero: 0.5

	ID=42

	1.0000 0.5000
	-0.5000 1.0000
	1.0000 1.0000
	1.0000 1.0000

	Input: {1,0,0,0,} Output: {0.731059,0.622459,}
	Input: {0,1,0,0,} Output: {0.377541,0.731059,}
	Input: {0,0,1,0,} Output: {0.731059,0.731059,}
	Input: {0,0,0,1,} Output: {0.731059,0.731059,}
	Input: {1,1,-1,1,} Output: {0.622459,0.817574,}

	Comparison values:
	 sigmoid(1.5) = 0.817574
	 sigmoid(1) = 0.731059
	 sigmoid(0.5) = 0.622459
	 sigmoid(-0.5) = 0.377541

	Testing low-level access
	Got shape (4, 2)
	Reading from memory pointed to by ANNDirect::weightsMatrix()...
	1 0.5
	-0.5 1
	1 1
	1 1
*/

#include <iostream>
#include <vector>
#include <tuple>

#include "../../ann/direct.h"
#include "../../ann/transferFunctions.h"

ANNNodeState sigmoid(ANNNodeState x)
{
//	return x>1. ? 1. : (x<0. ? 0. : x); // piecewise-linear transfer
	return logistic<ANNNodeState>(x); // from transferFunctions.h
}

int main(int argc, char** argv)
{
	ANNDirectHyperparameters hyp;
	hyp.inputNodes = 4;
	hyp.outputNodes = 2;
	hyp.transferFunction = sigmoid;

	std::cout << "Hyperparameters: " << hyp << std::endl << std::endl;

	ANNDirect nn0(hyp);
	nn0.getParameters("42 1 0.5 -0.5 1 1 1 1 1");
	nn0.print();
	std::vector<Percept> testInputs{{1,0,0,0}, {0,1,0,0}, {0,0,1,0}, {0,0,0,1}, {1,1,-1,1}};
	for(auto testInput : testInputs)
	{
		auto testOutput = nn0.output(testInput);
		std::cout << "Input: " << str(testInput) << " Output: " << str(testOutput) << std::endl;
	}
	std::cout << std::endl;

	std::vector<ANNNodeState> compVals{1.5, 1.0, 0.5, -0.5};
	std::cout << "Comparison values: " << std::endl;
	for(auto val : compVals)
		std::cout << " sigmoid(" << val << ") = " << sigmoid(val) << std::endl;

	std::cout << std::endl << "Testing low-level access" << std::endl;
	int inNodes, outNodes;
	std::tie(inNodes,outNodes) = nn0.shape();
	std::cout << "Got shape (" << inNodes << ", " << outNodes << ")" << std::endl;
	WeightsMatrix* wm = nn0.weightsMatrix();
	std::cout << "Reading from memory pointed to by ANNDirect::weightsMatrix()..." << std::endl;
	for(int i=0; i<inNodes; i++)
	{
		for(int j=0; j<outNodes; j++)
			std::cout << (*wm)[i][j] << " ";
		std::cout << std::endl;
	}
	return 0;
}
