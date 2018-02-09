#ifndef ARROWBOT_SIMULATOR_H
#define ARROWBOT_SIMULATOR_H

#include <iostream>
#include <string>
#include <boost/numeric/ublas/matrix.hpp>

#ifndef DM
#define DM if(DEBUG)
#endif // DM

#ifndef DEBUG
#define DEBUG false
#endif // DEBUG

#include "evclib/ann/direct.h"
#include "evclib/numericVector.h"

/* Class for evaluating Arrowbot controllers. Submit the controller with wire(),
   then run the simulation and evaluation computation with evaluateController().
   The simulation is implemented using GSL's ODE capabilities.
 */

using namespace boost::numeric::ublas;

typedef struct ArrowbotParameters
{
	int segments;
} ArrowbotParameters;

std::ostream& operator<<(std::ostream&, const ArrowbotParameters&);

typedef struct ArrowbotSimulationParameters
{
	double totalTime;
	double timeStep;
	vector<vector<double>> targetOrientations;
	vector<vector<double>> initialConditions;
	bool integrateError;
	bool writeTrajectories;
} ArrowbotSimulationParameters;

std::ostream& operator<<(std::ostream&, const ArrowbotSimulationParameters&);

class ArrowbotSimulator
{
	private:

	const ArrowbotParameters& botParameters;
	const ArrowbotSimulationParameters& simParameters;
	matrix<double> sensorAttachment;
	ANNDirect* currentController;
	matrix<double> phiCoefficient, psiCoefficient;

	void validateSensorPlacementArray(const std::vector<unsigned int>&);
	void validateArrowbotParameters();
	void validateArrowbotSimulationParameters();
	void validateController();
	void validateMorphology();
	void parseController(matrix<double>& W, matrix<double>& Y);
	double evaluateControllerForOrientations(int orientationsIdx);

	public:

	ArrowbotSimulator(const ArrowbotParameters& p, const ArrowbotSimulationParameters& sp) :
		botParameters(p),
		simParameters(sp),
		currentController(nullptr)
	{
		validateArrowbotParameters();
		validateArrowbotSimulationParameters();
	};
	void setSensorAttachmentMatrix(const matrix<double>& newAttachmentMatrix) {sensorAttachment = newAttachmentMatrix;};
	void placeSensors(NumericVector<unsigned>* newSensorPlacement);
	void wire(ANNDirect* newController);
	void evaluateController();
	inline unsigned segments(){return botParameters.segments;};
};

#endif // ARROWBOT_SIMULATOR_H
