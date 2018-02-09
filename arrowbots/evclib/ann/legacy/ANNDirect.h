#ifndef ANN_DIRECT_H
#define ANN_DIRECT_H

#include <string>
#include <array>
#include "../transferFunctions.h"

#ifndef ANN_DIRECT_INPUT_NODES
#define ANN_DIRECT_INPUT_NODES 4
#endif // ANN_DIRECT_INPUT_NODES

#ifndef ANN_DIRECT_OUTPUT_NODES
#define ANN_DIRECT_OUTPUT_NODES 2
#endif // ANN_DIRECT_OUTPUT_NODES

// The type to be used for ANN's nodes, including outputs and inputs
// It must be convertible to from double (i.e., understand assignments like =0.0)
#ifndef ANNNodeStateType
#define ANNNodeStateType float
#endif // ANNNodeStateType

#ifdef TANH_TRANSFER
#define ANN_DIRECT_SIGMOID(X) tanHyperbolic<ANNNodeStateType>(X) // from ../transferFunctions.h
#else // TANH_TRANSFER
#define ANN_DIRECT_SIGMOID(X) logistic<ANNNodeStateType>(X) // from ../transferFunctions.h
#endif // TANH_TRANSFER

typedef std::array<ANNNodeStateType,ANN_DIRECT_INPUT_NODES> Percept;
typedef std::array<ANNNodeStateType,ANN_DIRECT_OUTPUT_NODES> MotorPattern;

std::string str(const Percept& perc);
std::string str(const MotorPattern& motPat);

class NeuralNetwork
{
	private:

	ANNNodeStateType inputToOutput[ANN_DIRECT_INPUT_NODES][ANN_DIRECT_OUTPUT_NODES];

	public:

	int ID;
	double eval;
	NeuralNetwork(std::string);
	void print() const;
	std::string getDesc() const;
	MotorPattern output(const Percept& input) const; // depends on ANN_DIRECT_SIGMOID()
};

#endif // ANN_DIRECT_H
