#include <cstdlib>
#include <iostream>
#include <sstream>

#include <string.h>

#include "direct.h"
#include "../misc.h"

std::string str(const Percept& perc)
{
	std::ostringstream os;
	os << "{";
	for(auto s : perc)
		os << s << ",";
	os << "}";
	return os.str();
}

std::ostream& operator<<(std::ostream& os, const ANNDirectHyperparameters& hp)
{
  os << "input nodes: " << hp.inputNodes << " output nodes: " << hp.outputNodes << " transfer function at zero: " << hp.transferFunction(0.);
  return os;
}

ANNDirect::ANNDirect(const ANNDirectHyperparameters& hyp)
{
	hyperparameters = hyp;
	inputToOutput.resize(hyperparameters.inputNodes);
	for(auto it=inputToOutput.begin(); it!=inputToOutput.end(); it++)
		it->resize(hyperparameters.outputNodes);
}

void ANNDirect::getParameters(std::string genotype)
{
	const char* netdesc = genotype.c_str();

	// validating the string
	const int numWeights = hyperparameters.inputNodes*hyperparameters.outputNodes;
	const int dim = countSpaces(netdesc);
	if(dim != numWeights)
	{
		std::cerr << "Bad neural network string " << genotype << ". It must have exactly " << numWeights << " weights (it has " << dim << ")\n";
		exit(1);
	}

	// parsing the string
	int len = strlen(netdesc);
	char buf[len+2];
	strncpy(buf, netdesc, len+2);

	char* pch = strtok(buf, " ");
	sscanf(pch, "%d", &id); // assigning the ID
	ANNNodeState weightBuffer;
	for(int i=0; i<hyperparameters.inputNodes; i++)
		for(int j=0; j<hyperparameters.outputNodes; j++)
		{
			pch = strtok(NULL, " ");
			sscanf(pch, "%lf", &weightBuffer); // assigning the weights
			inputToOutput[i][j] = weightBuffer;
		}

	setEvaluation(-1.0); // customarily assigning the evaluation to -1
}

MotorPattern ANNDirect::output(const Percept& input) const
{
//	std::cout << "From network ";
//	print();
//	std::cout << std::endl << "Input vector:";
//	for(auto sensVal : input)
//		std::cout << " " << sensVal;
//	std::cout << std::endl;

	MotorPattern output(hyperparameters.outputNodes, 0.0);
	for(int i=0; i<hyperparameters.outputNodes; i++)
	{
		for(int j=0; j<hyperparameters.inputNodes; j++)
			output[i] += inputToOutput[j][i]*input[j];
		output[i] = hyperparameters.transferFunction(output[i]);
	}

//	std::cout << "Returning output";
//	for(auto motVal : output)
//		std::cout << " " << motVal;
//	std::cout << std::endl;

	return output;
}

void ANNDirect::print() const
{
	printf("ID=%d\n\n", id);
	for(int i=0; i<hyperparameters.inputNodes; i++)
	{
		for(int j=0; j<hyperparameters.outputNodes; j++)
			printf("%2.4f ", inputToOutput[i][j]);
		printf("\n");
	}
	printf("\n");
}

std::string ANNDirect::getDesc() const
{
	std::ostringstream ss;
	ss << id;
	for(int i=0; i<hyperparameters.inputNodes; i++)
		for(int j=0; j<hyperparameters.outputNodes; j++)
			ss << " " << inputToOutput[i][j];
	return ss.str();
}
