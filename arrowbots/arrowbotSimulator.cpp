#include <tuple>
#include <iostream>
#include <sstream>
#include <cstdlib>
#include <fstream>
#include <algorithm>
#include <vector>
#include <string>
#include <cmath>
#include <cstdlib>
#include <boost/numeric/ublas/io.hpp>
#include <boost/numeric/odeint.hpp>

#include "arrowbotSimulator.h"

/* Auxiliary functions */

void exitWithError(const std::string& mess)
{
	std::cerr << mess << std::endl;
	exit(EXIT_FAILURE);
}

void lowerTriangularOnes(matrix<double>& K, int size)
{
	K.resize(size, size);
	for(int i=0; i<size; i++)
		for(int j=0; j<size; j++)
			K(i,j) = i>=j ? 1. : 0.;
}

std::ostream& operator<<(std::ostream& os, const vector<vector<double>>& vv)
{
	for(unsigned i=0; i<vv.size(); i++)
		os << i << ": " << vv(i) << std::endl;
	return os;
}

/* Parameter structures IO functions */

std::ostream& operator<<(std::ostream& os, const ArrowbotParameters& p)
{
	os << "segments: " << p.segments << "\n";
	return os;
}

std::ostream& operator<<(std::ostream& os, const ArrowbotSimulationParameters& sp)
{
	os << "total time: " << sp.totalTime
	   << "\ntime step: " << sp.timeStep
	   << "\nintegrate error: " << sp.integrateError
	   << "\nwrite trajectories: " << sp.writeTrajectories
	   << "\nTarget orientations:\n" << sp.targetOrientations
	   << "\nInitial conditions:\n" << sp.initialConditions;
	return os;
}

/* ArrowbotSimulator class definitions */

// Private

void ArrowbotSimulator::validateArrowbotParameters()
{
	if(segments() < 1)
		exitWithError("Bad parameters: Arrowbot must have at least one segment. Exiting");
}

void ArrowbotSimulator::validateArrowbotSimulationParameters()
{
	if(simParameters.targetOrientations.size() == 0)
		exitWithError("Bad simulation parameters: no target orientations supplied. Exiting");
	if(simParameters.targetOrientations.size() != simParameters.initialConditions.size())
		exitWithError("Bad simulation parameters: initial conditions must be supplied for every target orientation. Exiting");
	if(simParameters.targetOrientations(0).size() != segments() ||
	   simParameters.initialConditions(0).size() != segments())
		exitWithError("Bad simulation parameters: size of target orientation or initial conditions vectors does not match the number of segments. Exiting");
	if(simParameters.totalTime < simParameters.timeStep)
		exitWithError("Bad simulation parameters: time step must be less than or equal to total simulation time. Exiting");
}

void ArrowbotSimulator::validateController()
{
	unsigned sensors, motors;
	std::tie(sensors, motors) = currentController->shape();
	if(sensors!=2*segments() || motors!=segments())
	{
		std::ostringstream os;
		os << "ANN size (" << sensors << ", " << motors << ") does not match robot size (" << 2*segments() << ", " << segments() << ", exiting";
		exitWithError(os.str());
	}
}

void ArrowbotSimulator::validateMorphology()
{
	unsigned maxSensorsPerSegment = 0;
	unsigned sensorsPerSegment = 0;
	for(unsigned i=0; i<segments(); i++)
	{
		for(unsigned j=0; j<segments(); j++)
		{
			if(sensorAttachment(i,j) != 0.)
			{
				if(sensorAttachment(i,j) != 1.)
					exitWithError("Bad parameters: attachment matrix must only contain zeros and ones. Exiting");
				sensorsPerSegment++;
			}
		}
		maxSensorsPerSegment = maxSensorsPerSegment>sensorsPerSegment ? maxSensorsPerSegment : sensorsPerSegment;
		sensorsPerSegment = 0;
	}
	if(maxSensorsPerSegment > 1)
		exitWithError("Bad parameters: having more than one sensor per segment is not supported. Exiting");
}

void ArrowbotSimulator::validateSensorPlacementArray(const std::vector<unsigned>& spa)
{
	if(spa.size() != segments())
		exitWithError("Sensor placement array too short, exiting.");
	for(auto it=spa.begin(); it!=spa.end(); it++)
		if(*it > segments())
			exitWithError("One of the elements of the sensor placement array is too large, exiting.");
}

void ArrowbotSimulator::parseController(matrix<double>& W, matrix<double>& Y)
{
	unsigned sensors, motors;
	std::tie(sensors, motors) = currentController->shape();
	W.resize(motors, motors, false);
	Y.resize(motors, motors, false);
	auto ptrWts = currentController->weightsMatrix();
	for(unsigned i=0; i<motors; i++)
		for(unsigned j=0; j<motors; j++)
		{
			W(i,j) = (*ptrWts)[i][j];
			Y(i,j) = (*ptrWts)[motors+i][j];
		}

	DM std::cout << "Parsing the controller:\n";
	DM std::cout << "W = " << W << " Y = " << Y << std::endl;
}

double ArrowbotSimulator::evaluateControllerForOrientations(int orientationsIdx)
{
	typedef vector<double> stateType;

	// Variables regulating the behavior of the RHS for large values of x
	static unsigned rhsOverflow;
	static unsigned rhsOverflowCounter;
	static const double rhsOverflowValue = 100.;
	static const unsigned rhsOverflowCheckPeriod = 40; // keep in mind that runge_kutta4 calls the method four times each step, and double has a pretty good range

	class ArrowbotRHS // WARNING: reset rhsOverflow to false before giving this to an integrator
	{
		const matrix<double>& m_phiCoefficient;
		stateType psiContrib;

		void checkForOverflow(const stateType& x)
		{
			rhsOverflowCounter++;
			if(rhsOverflowCounter == rhsOverflowCheckPeriod)
			{
				rhsOverflowCounter = 0;
				for(unsigned i=0; i<x.size(); i++)
					if(x(i) >= rhsOverflowValue || x(i) <= -1*rhsOverflowValue)
						rhsOverflow = true;
			}
		};

		public:

		ArrowbotRHS(const matrix<double>& phiCoeff, const matrix<double>& psiCoeff, const vector<double>& targetOrientations) :
			m_phiCoefficient(phiCoeff),
			psiContrib(prod(psiCoeff, targetOrientations)) {};

		void operator()(const stateType& x, stateType& dxdt, const double /* t */)
		{
			checkForOverflow(x);
			if(rhsOverflow)
				for(unsigned i=0; i<x.size(); i++)
					dxdt(i) = 0.; // Full stop!
			else
			{
				dxdt = psiContrib;
				axpy_prod(m_phiCoefficient, x, dxdt, false); // Proceed normally
			}
		};
	};

	class ArrowbotObserver
	{
		double& error;
		double currentAverageSquareError;
		double accumulatedAverageSquareError;
		const bool accumulate;
		matrix<double> K;
		stateType targetAbsAngles;
		double prevTime;
		bool firstCall; // needed because you just can't use NaNs with -ffast-math
		std::string trajectoryFileName;

		double totalSquareError(const stateType& curRelAngles)
		{
			stateType errors = targetAbsAngles - prod(K, curRelAngles);
			double accum = 0.;
			for(unsigned i=0; i<errors.size(); i++)
				accum += errors(i)*errors(i);
			return accum;
		};

		double averageSquareError(const stateType& curRelAngles)
		{
			return totalSquareError(curRelAngles)/double(curRelAngles.size());
		};

		double timeSinceLastCall(double t)
		{
			double dt = t - prevTime;
			prevTime = t;
			if(firstCall)
			{
				firstCall = false;
				return 0.;
			}
			else
				return dt;
		};

		public:

		ArrowbotObserver(const stateType& psi, double& err, bool accum=false, std::string trajFileName="") :
			error(err),
			currentAverageSquareError(0.),
			accumulatedAverageSquareError(0.),
			accumulate(accum),
			targetAbsAngles(psi),
			prevTime(0.),
			firstCall(true),
			trajectoryFileName(trajFileName)
		{
			lowerTriangularOnes(K, targetAbsAngles.size());
			if(!trajectoryFileName.empty())
			{
				std::ofstream ofs;
				ofs.open(trajectoryFileName, std::ofstream::out | std::ofstream::trunc);
				ofs.close();
			}
		};

		void operator()(const stateType& x, double t)
		{
			DM std::cout << "t: " << t << " state: " << x << std::endl;

			if(!trajectoryFileName.empty())
			{
				std::ofstream ofs;
				ofs.open(trajectoryFileName, std::ofstream::out | std::ofstream::app);
				ofs << std::setprecision(std::numeric_limits<double>::digits10 + 2) << t;
				for(unsigned i=0; i<x.size(); i++)
					ofs << " " << x(i);
				ofs << "\n";
				ofs.close();
			}

//			currentAverageSquareError = averageSquareError(x);
			currentAverageSquareError = totalSquareError(x);
			if(accumulate)
			{
				accumulatedAverageSquareError += currentAverageSquareError*timeSinceLastCall(t);
				error = accumulatedAverageSquareError;
			}
			else
				error = currentAverageSquareError;
		};
	};

	using namespace boost::numeric::odeint;

	stateType currentState = simParameters.initialConditions(orientationsIdx);
	runge_kutta4<stateType> stepper;

	rhsOverflow = false;
	ArrowbotRHS abtRHS(phiCoefficient, psiCoefficient, simParameters.targetOrientations(orientationsIdx));

	std::string filename = "";
	if(simParameters.writeTrajectories)
		filename = std::string("id") + std::to_string(currentController->getID()) + "env" + std::to_string(orientationsIdx) + ".trajectory";
	double error;

	ArrowbotObserver obs(simParameters.targetOrientations(orientationsIdx), error, simParameters.integrateError, filename);
	integrate_const(stepper, abtRHS, currentState, 0.0, simParameters.totalTime, simParameters.timeStep, obs);

	return -1.*log10(error);
}

// Public

void ArrowbotSimulator::placeSensors(NumericVector<unsigned>* newSensorPlacement)
{
	validateSensorPlacementArray(newSensorPlacement->vals);

	sensorAttachment = zero_matrix<double>(segments());
	for(unsigned i=0; i<segments(); i++)
	{
		unsigned curSensPos = (newSensorPlacement->vals)[i];
		if(curSensPos > 0)
			sensorAttachment(i, curSensPos-1) = 1;
	}
//	validateMorphology();

	DM std::cout << "Placed the sensors, attachment matrix is now J = " << sensorAttachment << "\n";
}

void ArrowbotSimulator::wire(ANNDirect* newController)
{
	// setting up the controller
	currentController = newController;
	validateController();
	matrix<double> Y, K;
	parseController(psiCoefficient, Y);
	lowerTriangularOnes(K, segments());
	K = prod(sensorAttachment, K);
	phiCoefficient = Y - prod(psiCoefficient, K);

	DM std::cout << "Results of wiring:\npsiCoefficient: " << psiCoefficient << "\nphiCoefficient: " << phiCoefficient << std::endl;
}

void ArrowbotSimulator::evaluateController()
{
	if(!currentController)
	{
		std::cerr << "Evaluation of an unwired Arrowbot attempted, exiting\n";
		exit(EXIT_FAILURE);
	}

	unsigned numEnv = simParameters.targetOrientations.size();
	double evalSum = 0.0;
	for(unsigned i=0; i<numEnv; i++)
	{
		evalSum += evaluateControllerForOrientations(i);
/*		if(evalSum < -10.)
		{
			evalSum = -10.*((double) numEnv);
			break;
		}*/
	}

	currentController->setEvaluation(evalSum/((double) numEnv));

	DM std::cout << "Current eval " << currentController->getEvaluation() << " for controller " << currentController->getID() << std::endl;
}
