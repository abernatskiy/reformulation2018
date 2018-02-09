#include <string>
#include <sstream>
#include <iostream>
#include <cstdlib>

#include "../environmentByNumber.h"
#include "../numericVector.h"
#include "../situatedController.h"

typedef SituatedControllerHyperparameters<EnvironmentByNumberHyperparameters,NumericVectorHyperparameters> SitContHyp;
typedef SituatedController<EnvironmentByNumber,NumericVector<int>,SitContHyp> SitCont;

void printSitContInfo(const SitCont& sc)
{
	std::cout << "Description: " << sc.getDesc() << std::endl
						<< "Description of the Environment: " << sc.getEnvDesc() << std::endl
						<< "Description of the Controller: " << sc.getContrDesc() << std::endl;
}

int main(int argc, char** argv)
{
	SitContHyp hyp;
	hyp.environmentFields = 1;
	hyp.environmentHyperparameters.numEnvironments = 3;

	SitCont sc0(hyp);
	sc0.getParameters("123 0 1 2 3");
	printSitContInfo(sc0);

	sc0.setEvaluation(9001.);
	std::cout << sc0.getID() << " " << sc0.getEvaluation() << "\n";

	return 0;
}
