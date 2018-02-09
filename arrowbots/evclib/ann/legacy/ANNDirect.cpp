#include <cstdlib>
#include <iostream>
#include <sstream>

#include <string.h>

#include "ANNDirect.h"
#include "../../misc.h"

std::string str(const Percept& perc)
{
	std::ostringstream os;
	os << "{";
	for(auto s : perc)
		os << s << ",";
	os << "}";
	return os.str();
}

std::string str(const MotorPattern& motPat)
{
	std::ostringstream os;
	os << "{";
	for(auto s : motPat)
		os << s << ",";
	os << "}";
	return os.str();
}

NeuralNetwork::NeuralNetwork(std::string genotype)
{
//	std::cout << "Constructiong a network with " << ANN_DIRECT_INPUT_NODES
//						<< " input nodes and " << ANN_DIRECT_OUTPUT_NODES << " output nodes\n";

	const char* netdesc = genotype.c_str();

	// validating the string
	int dim = countSpaces(netdesc);
	if(dim != ANN_DIRECT_INPUT_NODES*ANN_DIRECT_OUTPUT_NODES)
	{
		std::cout << "Bad neural network string - must have exactly " << ANN_DIRECT_INPUT_NODES*ANN_DIRECT_OUTPUT_NODES << " weights (has " << dim << std::endl;
		exit(1);
	}

	// parsing the string
	int len = strlen(netdesc);
	char buf[len+2];
	strncpy(buf, netdesc, len+2);

	char* pch = strtok(buf, " ");
	sscanf(pch, "%d", &ID);
	for(int i=0; i<ANN_DIRECT_INPUT_NODES; i++)
		for(int j=0; j<ANN_DIRECT_OUTPUT_NODES; j++)
		{
			pch = strtok(NULL, " ");
			sscanf(pch, "%f", &inputToOutput[i][j]);
		}

	eval = -1.f;
}

void NeuralNetwork::print() const
{
	printf("ID=%d\n\n", ID);

	for(int i=0; i<ANN_DIRECT_INPUT_NODES; i++)
	{
		for(int j=0; j<ANN_DIRECT_OUTPUT_NODES; j++)
			printf("%2.4f ", inputToOutput[i][j]);
		printf("\n");
	}
	printf("\n");
}

std::string NeuralNetwork::getDesc() const
{
	std::ostringstream ss;
	ss << ID;
	for(int i=0; i<ANN_DIRECT_INPUT_NODES; i++)
		for(int j=0; j<ANN_DIRECT_OUTPUT_NODES; j++)
			ss << " " << inputToOutput[i][j];

	return ss.str();
}

MotorPattern NeuralNetwork::output(const Percept& input) const
{
//	std::cout << "From network ";
//	print();
//	std::cout << std::endl << "Input vector:";
//	for(auto sensVal : input)
//		std::cout << " " << sensVal;
//	std::cout << std::endl;

	MotorPattern output;
	output.fill(0.f);
	for(int i=0; i<ANN_DIRECT_OUTPUT_NODES; i++)
	{
		for(int j=0; j<ANN_DIRECT_INPUT_NODES; j++)
			output[i] += inputToOutput[j][i]*input[j];
		output[i] = ANN_DIRECT_SIGMOID(output[i]);
	}

//	std::cout << "Returning output";
//	for(auto motVal : output)
//		std::cout << " " << motVal;
//	std::cout << std::endl;

	return output;
}
