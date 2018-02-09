#ifndef EVCLIB_ENVIRONMENT_BY_NUMBER_H
#define EVCLIB_ENVIRONMENT_BY_NUMBER_H

#include <cstdlib>
#include <iostream>

#include "numericVector.h"

typedef struct EnvironmentByNumberHyperparameters
{
	unsigned numEnvironments;
} EnvironmentByNumberHyperparameters;

class EnvironmentByNumber : public NumericVector<int>
{
private:
	EnvironmentByNumberHyperparameters hyp;
public:
	EnvironmentByNumber(const EnvironmentByNumberHyperparameters& hp) : hyp(hp) {};
	void getParameters(std::string genotype)
	{
		NumericVector<int>::getParameters(genotype);
		if(vals.size() != 1)
		{
			std::cerr << "EnvironmentByNumber class requires exactly one parameter in genotype. Got genotype " << genotype << ", in which " << vals.size() << " fields were detected\n";
			exit(EXIT_FAILURE);
		}
		if(vals[0] < 0 || vals[0] >= hyp.numEnvironments)
		{
			std::cerr << "Environment number out of bounds for genotype " << genotype << " (must be between 0 and " << hyp.numEnvironments-1 << ")\n";
			exit(EXIT_FAILURE);
		}
	};
	int getEnvNum() const {return vals[0];};
};

#endif // EVCLIB_ENVIRONMENT_BY_NUMBER_H
