#include <string.h>
#include <sstream>

#include "ANNHiddenRecursive.h"
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
	const char* netdesc = genotype.c_str();

	// validating the string
	int strDim = countSpaces(netdesc);
	const int intendedDim = ANN_HIDDEN_RECURSIVE_HIDDEN_NODES*
		(ANN_HIDDEN_RECURSIVE_INPUT_NODES+ANN_HIDDEN_RECURSIVE_HIDDEN_NODES+ANN_HIDDEN_RECURSIVE_OUTPUT_NODES);
	if(strDim != intendedDim)
	{
		printf("Bad neural network string - number of fields must be exactly %d (it is %d)\n", intendedDim, strDim);
		exit(1);
	}

	// initializing values of the hidden layer
	resetHidden();

	// parsing the description string
	int len = strlen(netdesc);
	char buf[len+2];
	strncpy(buf, netdesc, len+2);

	char* pch = strtok(buf, " ");
	sscanf(pch, "%d", &ID);
	for(int i=0; i<ANN_HIDDEN_RECURSIVE_INPUT_NODES; i++)
		for(int j=0; j<ANN_HIDDEN_RECURSIVE_HIDDEN_NODES; j++)
		{
			pch = strtok(NULL, " ");
			sscanf(pch, "%f", &inputToHidden[i][j]);
		}
	for(int i=0; i<ANN_HIDDEN_RECURSIVE_HIDDEN_NODES; i++)
		for(int j=0; j<ANN_HIDDEN_RECURSIVE_HIDDEN_NODES; j++)
		{
			pch = strtok(NULL, " ");
			sscanf(pch, "%f", &hiddenToHidden[i][j]);
		}
	for(int i=0; i<ANN_HIDDEN_RECURSIVE_HIDDEN_NODES; i++)
		for(int j=0; j<ANN_HIDDEN_RECURSIVE_OUTPUT_NODES; j++)
		{
			pch = strtok(NULL, " ");
			sscanf(pch, "%f", &hiddenToOutput[i][j]);
		}

	eval = -1.f;
}

NeuralNetwork::NeuralNetwork(const NeuralNetwork& other) :
	ID(other.ID), eval(other.eval)
{
	// allocating memory and initializing values of the hidden layer
	for(int i=0; i<ANN_HIDDEN_RECURSIVE_HIDDEN_NODES; i++)
		hidden[i] = other.hidden[i];

	// allocating memory for inter-layer matrices
	for(int i=0; i<ANN_HIDDEN_RECURSIVE_INPUT_NODES; i++)
		for(int j=0; j<ANN_HIDDEN_RECURSIVE_HIDDEN_NODES; j++)
			inputToHidden[i][j] = other.inputToHidden[i][j];

	for(int i=0; i<ANN_HIDDEN_RECURSIVE_HIDDEN_NODES; i++)
		for(int j=0; j<ANN_HIDDEN_RECURSIVE_HIDDEN_NODES; j++)
			hiddenToHidden[i][j] = other.hiddenToHidden[i][j];

	for(int i=0; i<ANN_HIDDEN_RECURSIVE_HIDDEN_NODES; i++)
		for(int j=0; j<ANN_HIDDEN_RECURSIVE_OUTPUT_NODES; j++)
			hiddenToOutput[i][j] = other.hiddenToOutput[i][j];
}

void NeuralNetwork::print() const
{
	printf("ID=%d k=%d\n\n", ID, ANN_HIDDEN_RECURSIVE_HIDDEN_NODES);

	for(int i=0; i<ANN_HIDDEN_RECURSIVE_INPUT_NODES; i++)
	{
		for(int j=0; j<ANN_HIDDEN_RECURSIVE_HIDDEN_NODES; j++)
			printf("%2.4f ", inputToHidden[i][j]);
		printf("\n");
	}
	printf("\n");

	for(int i=0; i<ANN_HIDDEN_RECURSIVE_HIDDEN_NODES; i++)
	{
		for(int j=0; j<ANN_HIDDEN_RECURSIVE_HIDDEN_NODES; j++)
			printf("%2.4f ", hiddenToHidden[i][j]);
		printf("\n");
	}
	printf("\n");

	for(int i=0; i<ANN_HIDDEN_RECURSIVE_HIDDEN_NODES; i++)
	{
		for(int j=0; j<ANN_HIDDEN_RECURSIVE_OUTPUT_NODES; j++)
			printf("%2.4f ", hiddenToOutput[i][j]);
		printf("\n");
	}
	printf("\n");

	printf("Current values of the hidden layer:\n");
	printHidden();
}

void NeuralNetwork::printHidden() const
{
	for(int j=0; j<ANN_HIDDEN_RECURSIVE_HIDDEN_NODES; j++)
		printf(" %2.4f", hidden[j]);
	printf("\n");
}

std::string NeuralNetwork::getDesc() const
{
	char* buffer;
	const int buflen = 15;
	char tmpstr[buflen];
	sprintf(tmpstr, "%d ", ID);
	strncpy(buffer, tmpstr, buflen);

	for(int i=0; i<ANN_HIDDEN_RECURSIVE_INPUT_NODES; i++)
		for(int j=0; j<ANN_HIDDEN_RECURSIVE_HIDDEN_NODES; j++)
		{
			sprintf(tmpstr, "%2.4f ", inputToHidden[i][j]);
			strncat(buffer, tmpstr, buflen);
		}
	for(int i=0; i<ANN_HIDDEN_RECURSIVE_HIDDEN_NODES; i++)
		for(int j=0; j<ANN_HIDDEN_RECURSIVE_HIDDEN_NODES; j++)
		{
			sprintf(tmpstr, "%2.4f ", hiddenToHidden[i][j]);
			strncat(buffer, tmpstr, buflen);
		}
	for(int i=0; i<ANN_HIDDEN_RECURSIVE_HIDDEN_NODES; i++)
		for(int j=0; j<ANN_HIDDEN_RECURSIVE_OUTPUT_NODES; j++)
		{
			if(i==ANN_HIDDEN_RECURSIVE_HIDDEN_NODES-1 && j==1)
				sprintf(tmpstr, "%2.4f\n", hiddenToOutput[i][j]);
			else
				sprintf(tmpstr, "%2.4f ", hiddenToOutput[i][j]);
			strncat(buffer, tmpstr, buflen);
		}
	return std::string(buffer);
}

void NeuralNetwork::resetHidden()
{
//	printf("Resetting state %le %le to zeros\n", hidden[0], hidden[1]);
	for(int i=0; i<ANN_HIDDEN_RECURSIVE_HIDDEN_NODES; i++)
		hidden[i] = 0.f;
}

MotorPattern NeuralNetwork::output(const Percept& input)
{
	static ANNNodeStateType newHidden[ANN_HIDDEN_RECURSIVE_HIDDEN_NODES];
	for(int j=0; j<ANN_HIDDEN_RECURSIVE_HIDDEN_NODES; j++)
	{
		newHidden[j] = 0.f;
		for(int i=0; i<ANN_HIDDEN_RECURSIVE_INPUT_NODES; i++)
			newHidden[j] += inputToHidden[i][j]*input[i];
		for(int i=0; i<ANN_HIDDEN_RECURSIVE_HIDDEN_NODES; i++)
			newHidden[j] += hiddenToHidden[i][j]*hidden[i];
		newHidden[j] = ANN_HIDDEN_RECURSIVE_SIGMOID(newHidden[j]);
	}
	for(int i=0; i<ANN_HIDDEN_RECURSIVE_HIDDEN_NODES; i++)
		hidden[i] = newHidden[i];

	MotorPattern output;
	output.fill(0.f);
	for(int j=0; j<ANN_HIDDEN_RECURSIVE_OUTPUT_NODES; j++)
	{
		for(int i=0; i<ANN_HIDDEN_RECURSIVE_HIDDEN_NODES; i++)
			output[j] += hiddenToOutput[i][j]*hidden[i];
		output[j] = ANN_HIDDEN_RECURSIVE_SIGMOID(output[j]);
	}

	#ifdef TANH_TRANSFER
	for(auto& motorVal : output)
		motorVal = 0.5 + 0.5*motorVal;
	#endif // TANH_TRANSFER

	return output;
}
