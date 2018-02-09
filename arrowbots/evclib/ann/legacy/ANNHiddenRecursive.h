#ifndef ANN_HIDDEN_RECURSIVE
#define ANN_HIDDEN_RECURSIVE

#include <string>
#include <array>
#include "../transferFunctions.h"

#ifndef ANN_HIDDEN_RECURSIVE_INPUT_NODES
#define ANN_HIDDEN_RECURSIVE_INPUT_NODES 4
#endif // ANN_HIDDEN_RECURSIVE_INPUT_NODES

#ifndef ANN_HIDDEN_RECURSIVE_HIDDEN_NODES
#define ANN_HIDDEN_RECURSIVE_HIDDEN_NODES 2
#endif // ANN_HIDDEN_RECURSIVE_HIDDEN_NODES

#ifndef ANN_HIDDEN_RECURSIVE_OUTPUT_NODES
#define ANN_HIDDEN_RECURSIVE_OUTPUT_NODES 2
#endif // ANN_HIDDEN_RECURSIVE_OUTPUT_NODES

// The type to be used for ANN's nodes, including outputs and inputs
// It must be convertible to from double (i.e., understand assignments like =0.0)
#ifndef ANNNodeStateType
#define ANNNodeStateType float
#endif // ANNNodeStateType

#ifdef TANH_TRANSFER
#define ANN_HIDDEN_RECURSIVE_SIGMOID(X) tanHyperbolic<ANNNodeStateType>(X) // from ../transferFunctions.h
#else // TANH_TRANSFER
#define ANN_HIDDEN_RECURSIVE_SIGMOID(X) logistic<ANNNodeStateType>(X) // from ../transferFunctions.h
#endif // TANH_TRANSFER

typedef std::array<ANNNodeStateType,ANN_HIDDEN_RECURSIVE_INPUT_NODES> Percept;
typedef std::array<ANNNodeStateType,ANN_HIDDEN_RECURSIVE_OUTPUT_NODES> MotorPattern;

std::string str(const Percept& perc);
std::string str(const MotorPattern& motPat);

class NeuralNetwork
{
	private:

	ANNNodeStateType hidden[ANN_HIDDEN_RECURSIVE_HIDDEN_NODES];
	ANNNodeStateType inputToHidden[ANN_HIDDEN_RECURSIVE_INPUT_NODES][ANN_HIDDEN_RECURSIVE_HIDDEN_NODES];
	ANNNodeStateType hiddenToHidden[ANN_HIDDEN_RECURSIVE_HIDDEN_NODES][ANN_HIDDEN_RECURSIVE_HIDDEN_NODES];
	ANNNodeStateType hiddenToOutput[ANN_HIDDEN_RECURSIVE_HIDDEN_NODES][ANN_HIDDEN_RECURSIVE_OUTPUT_NODES];

	public:

	int ID;
	double eval;
	NeuralNetwork(std::string);
	NeuralNetwork(const NeuralNetwork&);
	void print() const;
	void printHidden() const;
	std::string getDesc() const;
	void resetHidden();
	MotorPattern output(const Percept& input); // depends on ANN_DIRECT_SIGMOID()
};

#endif // ANN_HIDDEN_RECURSIVE
