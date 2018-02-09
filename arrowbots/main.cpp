#include <iostream>
#include <tuple>
#include <cstdlib>
#include <fstream>
#include <sstream>

#include <boost/numeric/ublas/matrix.hpp>

#include "inih/cpp/INIReader.h"

#include "evclib/parseCLI.h"
#include "evclib/evalQueue.h"

#include "evclib/situatedController.h"
#include "evclib/numericVector.h"

#define ANNNodeState double // explicitly reminding ANNDirect which type we want (double is currently the default)
#include "evclib/ann/direct.h"

#include "arrowbotSimulator.h"

#ifndef DM
#define DM if(DEBUG)
#endif // DM

#ifndef DEBUG
#define DEBUG false
#endif // DEBUG

void loadVectorsFromFile(std::string filename, vector<vector<double>>& vectors, unsigned dim)
{
	std::ifstream ifs;
	ifs.open(filename, std::ifstream::in);
	if(!ifs)
	{
		std::cout << "Couldn't load " << filename << ", exiting\n";
		exit(EXIT_FAILURE);
	}
	std::string line;
	unsigned lineCount = 0;
	while(std::getline(ifs, line))
	{
		lineCount++;
		vectors.resize(lineCount, true);
		vectors(lineCount-1).resize(dim);
		std::istringstream iss(line);
		for(unsigned i=0; i<dim; i++)
		{
			if(!iss)
			{
				std::cout << "Vector of insufficient dimensionality provided, exiting\n";
				exit(EXIT_FAILURE);
			}
			iss >> vectors(lineCount-1)(i);
		}
		double streamTest;
		iss >> streamTest;
		if(iss)
		{
			std::cout << "Dimensionality of the provided vector too large, exiting\n";
			exit(EXIT_FAILURE);
		}
	}
	ifs.close();
}

int main(int argc, char** argv)
{
	// Parsing the command line to get input file names
	std::string inFN, outFN;
	std::tie(inFN, outFN) = parsecli::twoFilenamesForIO(argc, argv, "arrowBotEvaluator");

	// Reading the main configuration file
	std::string configFileName("arrowbot.ini");
	INIReader configReader(configFileName);
	if(configReader.ParseError() < 0)
	{
		std::cout << "Couldn't load " << configFileName << ", exiting\n";
		exit(EXIT_FAILURE);
	}

	// Creating the simulator for the robot
	// Loading the robot parameters
	ArrowbotParameters abtParams;
	const std::string abtParamsSectionName("arrowbot parameters");
	abtParams.segments = configReader.GetInteger(abtParamsSectionName, "segments", 2);
	std::cout << "Robot parameters:" << std::endl << abtParams << std::endl;

	// Figuring out how the morphology will be determined - GLOBAL
	std::string sensorAttachmentType = configReader.Get(abtParamsSectionName, "sensorAttachmentType", "identity");

	// Loading the simulation parameters
	ArrowbotSimulationParameters abtSimParams;
	const std::string abtSimParamsSectionName("simulation parameters");
	abtSimParams.totalTime = configReader.GetReal(abtSimParamsSectionName, "simulationTime", 1.0);
	abtSimParams.timeStep = configReader.GetReal(abtSimParamsSectionName, "timeStep", 0.1);
	abtSimParams.integrateError = configReader.GetBoolean(abtSimParamsSectionName, "integrateError", false);
	abtSimParams.writeTrajectories = configReader.GetBoolean(abtSimParamsSectionName, "writeTrajectories", false);
	loadVectorsFromFile("targetOrientations.dat", abtSimParams.targetOrientations, abtParams.segments);
	loadVectorsFromFile("initialConditions.dat", abtSimParams.initialConditions, abtParams.segments);

	std::cout << "Simulation parameters:" << std::endl << abtSimParams << std::endl;

	ArrowbotSimulator abts(abtParams, abtSimParams);

	if(sensorAttachmentType.compare("variable") == 0)
	{
		typedef SituatedControllerHyperparameters<NumericVectorHyperparameters,ANNDirectHyperparameters> EmbContHyp;
		typedef SituatedController<NumericVector<unsigned>,ANNDirect,EmbContHyp> EmbCont;

		// Describing the compound genotype : for N segments, N integer values between 0 and N are needed to describe the morphology, the rest is the controller
		EmbContHyp hyp;
		hyp.environmentFields = abts.segments();
		hyp.controllerHyperparameters.inputNodes = 2*abts.segments();
		hyp.controllerHyperparameters.outputNodes = abts.segments();
		hyp.controllerHyperparameters.transferFunction = [](double x){return x;}; // Purely linear controller. Note that the controller is never used to actually transform sensor inputs to motor outputs, i.e. this setting does not influence anything

		// Creating the evaluation queue and drawing the rest of the owl:
		auto evalQueue = EvalQueue<EmbCont,EmbContHyp>(inFN, outFN, hyp);

		while(1)
		{
			auto ptrEmbContr = evalQueue.getNextPhenotypePtr();
			abts.placeSensors(&(ptrEmbContr->env)); // Sensors are placed separately for each individual
			abts.wire(&(ptrEmbContr->contr));
			abts.evaluateController();

			// Since only the controller part gets evaluated by default, we need to copy the evaluation to the field of the composite object EmbCont
			ptrEmbContr->setEvaluation((ptrEmbContr->contr).getEvaluation());
		}
	}
	else
	{
		// Placing the sensors once for all simulations
		if(sensorAttachmentType.compare("identity") == 0)
			abts.setSensorAttachmentMatrix(identity_matrix<double>(abts.segments()));
		else if(sensorAttachmentType.compare("null") == 0)
			abts.setSensorAttachmentMatrix(zero_matrix<double>(abts.segments()));
		else
		{
			std::cout << "Three types of sensor attachment are available:\n"
			        << " * identity - each sensor is attached to its own segment\n"
			        << " * null - all sensors are attached to the fixed segment\n"
			        << " * variable - sensor attachment matrix will be parsed from the genotype/individual string\n"
			        << "Neither of these matched the type in the configuration file (" << sensorAttachmentType << "), exiting\n";
			exit(EXIT_FAILURE);
		}

		// Describing the Arrowbot's controller: two sensors and one motor per segment, identity as transfer function for a purely linear controller
		ANNDirectHyperparameters hyp;
		hyp.inputNodes = 2*abts.segments();
		hyp.outputNodes = abts.segments();
		hyp.transferFunction = [](double x){return x;}; // purely linear controller

		// Creating the evaluation queue and doing the simulations
		auto evalQueue = EvalQueue<ANNDirect,ANNDirectHyperparameters>(inFN, outFN, hyp);

		while(1)
		{
			auto ptrANN = evalQueue.getNextPhenotypePtr();
			abts.wire(ptrANN);
			abts.evaluateController();
		}
	}

	return 0;
}
