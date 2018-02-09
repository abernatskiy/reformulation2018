#include <iostream>

#include "../environmentByNumber.h"

int main(int argc, char** argv)
{
	EnvironmentByNumberHyperparameters hyp;
	hyp.numEnvironments = 5;

	EnvironmentByNumber e0(hyp);
	e0.getParameters("11 3");
	std::cout << e0.getDesc() << std::endl;

	e0.setEvaluation(1000.);
	std::cout << e0.getEvaluation() << std::endl;

	EnvironmentByNumber e1(hyp);
//	e1.getParameters("12");
//	e1.getParameters("13 4 5");
	e1.getParameters("14 6");

	return 0;
}
