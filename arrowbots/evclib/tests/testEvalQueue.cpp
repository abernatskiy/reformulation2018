#include <iostream>
#include <string>

#define QUEUE_VEROBOSE_EVALUATION

#include "../evalQueue.h"

class TestPhenotype
{
public:
	std::string phenotype;
	double alpha;

	int id;
	double eval;

	TestPhenotype(double a) : id(0), alpha(a) {};
	void getParameters(std::string s) {phenotype = s + " phenotype";};
	std::string getDesc() {return "desc: " + phenotype + " eval: " + std::to_string(eval) + " id: " + std::to_string(id);};
};

int main(int argc, char** argv)
{
	auto eq = EvalQueue<TestPhenotype,double>("/tmp/indiv", "/tmp/evals", 42);
	for(int i=0; i<20; i++)
	{
		std::cout << "Current queue:" << std::endl;
		eq.print();
		std::cout << std::endl << std::endl;

		auto phPtr = eq.getNextPhenotypePtr();
		phPtr->eval = (double) phPtr->phenotype.size();
	}
	std::cout << "That's all" << std::cout;
	return 0;
}
