/* Template for the evaluation queue class

   Upon instantiaition, genotypes to evaluate are read from the input file
   (separated by newlines). For each genotype, an Individual object is
   constructed with a constant set of hyperparameters, their parameters
   are read from genotype strings and they are added to the queue.
   The user is then expected to evaluate each of these objects using
   pointers returned by getNextPhenotypePtr(). Evaluations are expected to
   be stored withing the objects via setEvaluation(double) calls.
   When all the genotypes have been evaluated, getNextPhenotypePtr() call,
   before performing its normal functions, also writes the evaluations
   into the output file and reads the input file once again.

   TL;DR Just make an instance using a pair of pipes as IO files and
   evaluate away with getNextPhenotypePtr().

   Individual classes bust comply to the BaseIndividual interface
   (see baseIndividual.h).

   Defining QUEUE_VERBOSE_EVALUATION enables stdout reports before each
   evaluation.
*/

#ifndef EVCLIB_EVAL_QUEUE_H
#define EVCLIB_EVAL_QUEUE_H

#include <string>
#include <vector>

#ifndef MAX_GENOME_LENGTH
#define MAX_GENOME_LENGTH 10000
#endif // MAX_GENOME_LENGTH

#ifndef MAX_QUEUE_LENGTH
#define MAX_QUEUE_LENGTH 500
#endif // MAX_QUEUE_LENGTH

#ifndef EVALUATION_PRECISION
#define EVALUATION_PRECISION 10 // digits after a decimal in the significand/mantissa
#endif // EVALUATION_PRECISION

template<class Phenotype, class Hyperparameters>
class EvalQueue
{
private:
	std::string inputFileName;
	std::string outputFileName;
	std::vector<Phenotype> queue;
	unsigned curPos;
	void readInput();
	void writeOutput();
	Hyperparameters hyperparameters;
public:
	EvalQueue(std::string inputFN, std::string outputFN, const Hyperparameters& hp);
	Phenotype* getNextPhenotypePtr();
	void print();
};

// DEFINITIONS

#include <fstream>
#include <iostream>
#include <cstdlib>
#include <iomanip>

template<class Phenotype, class Hyperparameters>
EvalQueue<Phenotype,Hyperparameters>::EvalQueue(std::string inputFN, std::string outputFN, const Hyperparameters& hp) :
	inputFileName(inputFN),
	outputFileName(outputFN),
	hyperparameters(hp)
{
	readInput();
}

template<class Phenotype, class Hyperparameters>
void EvalQueue<Phenotype,Hyperparameters>::readInput()
{
	std::ifstream inputFile;
	inputFile.open(inputFileName);
	if(!inputFile.is_open())
	{
		std::cerr << "Cannot open the input\n";
		exit(EXIT_FAILURE);
	}

	std::string curLine;
	int counter = 0;

	while(std::getline(inputFile, curLine))
	{
#ifdef MAX_QUEUE_LENGHT
		if(counter == MAX_QUEUE_LENGTH)
		{
			std::cerr << "Queue too big, exiting\n";
			exit(EXIT_FAILURE);
		}
#endif // MAX_QUEUE_LENGTH
		queue.emplace_back(hyperparameters);
		auto itLastElem = std::prev(queue.end());
		itLastElem->getParameters(curLine);
		counter++;
	}
	inputFile.close();

	curPos = 0;
}

template<class Phenotype, class Hyperparameters>
void EvalQueue<Phenotype,Hyperparameters>::writeOutput()
{
	std::ofstream outputFile;
	outputFile.open(outputFileName);
	if(!outputFile.is_open())
	{
		std::cerr << "Cannot open the output\n";
		exit(EXIT_FAILURE);
	}

	for(auto it=queue.begin(); it!=queue.end(); it++)
		outputFile << it->getID() << " " << std::scientific << std::setprecision(EVALUATION_PRECISION) << it->getEvaluation() << std::endl;
	outputFile.close();

//	std::cout << "cylindersEvasion: wrote evaluations for a queue of " << queue.size() << " individuals\n";
	queue.clear();
}

template<class Phenotype, class Hyperparameters>
Phenotype* EvalQueue<Phenotype,Hyperparameters>::getNextPhenotypePtr()
{
	if(curPos == queue.size())
	{
		writeOutput();
		readInput();
	}

	auto it = queue.begin() + curPos;
	Phenotype* ptr = &(*it);

#ifdef QUEUE_VERBOSE_EVALUATION
	std::cout << "Evaluating " << it->getDesc() << std::endl << std::flush;
#endif // QUEUE_VERBOSE_EVALUATION

	curPos++;
	return ptr;
}

template<class Phenotype, class Hyperparameters>
void EvalQueue<Phenotype,Hyperparameters>::print()
{
	std::cout << "Queue is at " << curPos << ". Total size is " << queue.size() << std::endl;
	for(auto it=queue.begin(); it!=queue.end(); it++)
		std::cout << it->getDesc() << std::endl;
}

#endif // EVCLIB_EVAL_QUEUE_H
