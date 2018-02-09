#ifndef EVCLIB_ANN_DIRECT_H
#define EVCLIB_ANN_DIRECT_H

#include <string>
#include <vector>
#include <functional>
#include <tuple>
#include <iostream>

#include "../baseIndividual.h"

// The type to be used for ANN's nodes, including outputs and inputs
// It must be convertible to from double (i.e., understand assignments like =0.0)
#ifndef ANNNodeState
#define ANNNodeState double
#endif // ANNNodeStateType

typedef struct ANNDirectHyperparameters
{
	int inputNodes;
	int outputNodes;
	std::function<ANNNodeState(ANNNodeState)> transferFunction;
} ANNDirectHyperparameters;

std::ostream& operator<<(std::ostream& os, const ANNDirectHyperparameters& hp);

typedef std::vector<ANNNodeState> Percept;
typedef std::vector<ANNNodeState> MotorPattern;
typedef std::vector<std::vector<ANNNodeState>> WeightsMatrix; // same type is used for node state and weights

std::string str(const Percept& perc); // works for MotorPatterns as well

class ANNDirect : public BaseIndividual
{
private:
	ANNDirectHyperparameters hyperparameters;
	WeightsMatrix inputToOutput;

public:
	ANNDirect(const ANNDirectHyperparameters&);
	void getParameters(std::string);
	MotorPattern output(const Percept& input) const;

	void print() const;
	std::string getDesc() const;

	double inputToOutputWeight(int i, int o){return inputToOutput[i][o];};
	int inputNodes(){return hyperparameters.inputNodes;};
	int outputNodes(){return hyperparameters.outputNodes;};

	// low level access
	std::pair<int,int> shape(){return std::make_pair(hyperparameters.inputNodes, hyperparameters.outputNodes);};
	WeightsMatrix* weightsMatrix(){return &inputToOutput;};
};

#endif // EVCLIB_ANN_DIRECT_H
