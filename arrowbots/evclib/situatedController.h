/* Individual class consisting of an Environment and a
   Controller. Compatible with EvalQueue template.

   Constructs from a SituatedControllerHyperparameters
   object (see below).

   Can read parameters from line of the following format:

   ID envf1 .. envfN contr_desc

   where:

     ID is the ID of the phenotype.

     envf0 to envfN-1 are text fields describing the
       environment in which the controller is to be
       evaluated. N, the number of the text fields,
       is controlled by the environmentFields member
       of the SituatedControllerHyperparameters class.

     contr_desc is the text data (possibly consisting
       of fields) describing the controller to be
       evaluated.

     ' ' is the field separator defined by the
       FIELD_SEPARATOR define directive.

   Controller and Environment must be
   BaseIndividual-compliant classes,
   see baseIndividual.h.
   Method getParameters(string) must be compatible with
   the EVS string format:

     ID envf0 .. envfN-1 for Environment
     ID contr_descr for Controller

   Additionally, Environment class must be able to
   process empty genotypes (with zero fields)
   if support of N=0 situation is desirable.
*/

#ifndef EVCLIB_SITUATED_CONTROLLER_H
#define EVCLIB_SITUATED_CONTROLLER_H

#include <string>
#include <sstream>
#include <vector>
#include <iostream>
#include <cstdlib>

#include "baseIndividual.h"

#ifndef FIELD_SEPARATOR
#define FIELD_SEPARATOR ' '
#endif // FIELD_SEPARATOR

template<class EnvironmentHyperparameters, class ControllerHyperparameters>
class SituatedControllerHyperparameters
{
public:
	int environmentFields; // the rest of the genotype is assumed to define a controller
	EnvironmentHyperparameters environmentHyperparameters;
	ControllerHyperparameters controllerHyperparameters;
};

template<class Environment, class Controller, class SituatedControllerHyperparameters>
class SituatedController : public BaseIndividual
{
private:
	SituatedControllerHyperparameters hyp;
public:
	Environment env;
	Controller contr;
	SituatedController(const SituatedControllerHyperparameters& hp);
	void getParameters(std::string);
	std::string getDesc() const;
	std::string getContrDesc() const {return contr.getDesc();};
	std::string getEnvDesc() const {return env.getDesc();};
};

// DEFINITIONS

template<class Environment, class Controller, class SituatedControllerHyperparameters>
SituatedController<Environment,Controller,SituatedControllerHyperparameters>::SituatedController(const SituatedControllerHyperparameters& hp) :
	hyp(hp),
	env(hp.environmentHyperparameters),
	contr(hp.controllerHyperparameters) {}

template<class Environment, class Controller, class SituatedControllerHyperparameters>
void SituatedController<Environment,Controller,SituatedControllerHyperparameters>::getParameters(std::string fullGenotype)
{
	// separate the full genotype into strings for ID, environment fields anf the rest of stuff
	std::stringstream ss(fullGenotype);

	std::string idStr;
	std::getline(ss, idStr, FIELD_SEPARATOR);

	std::vector<std::string> envFields;
	std::string field;
	for(int i=0; i<hyp.environmentFields; i++)
	{
		std::getline(ss, field, FIELD_SEPARATOR); // FIXME: check if there are enough fields
		envFields.push_back(field);
	}

	std::string contrDesc;
	std::getline(ss, contrDesc);

	// std::cout << "Parsed the fullGenotype into the following parts:" << std::endl
	// 					<< "ID: " << idStr << std::endl
	// 					<< "Environment fields:";
	// for(auto it: envFields)
	// 	std::cout << " " << it;
	// std::cout << std::endl
	// 					<< "Controller desc: " << contrDesc << std::endl;

	// reading the ID
	id = std::stoi(idStr);

	// customarily assigning initial evaluation to -1.0
	setEvaluation(-1.0);

	// bringing Environment's genome together and forwarding to the Environment instance
	std::ostringstream envGenSS;
	envGenSS << idStr;
	for(auto envField: envFields)
		envGenSS << " " << envField;
	env.getParameters(envGenSS.str());

	// same for the Controller instance
	std::ostringstream contrGenSS;
	contrGenSS << idStr << FIELD_SEPARATOR << contrDesc;
	contr.getParameters(contrGenSS.str());
}

template<class Environment, class Controller, class SituatedControllerHyperparameters>
std::string SituatedController<Environment,Controller,SituatedControllerHyperparameters>::getDesc() const
{
	std::string envID, envDesc, contrID, contrDesc;

	std::stringstream envStream(env.getDesc());
	std::getline(envStream, envID, FIELD_SEPARATOR);
	std::getline(envStream, envDesc);

	std::stringstream contrStream(contr.getDesc());
	std::getline(contrStream, contrID, FIELD_SEPARATOR);
	std::getline(contrStream, contrDesc);

	if(envID.compare(contrID) != 0)
	{
		std::cout << "IDs of Environment and Controller are different within the same SituatedController\n" <<
			"Most likely, this is due to some memory corruption. Exiting.\n";
		exit(EXIT_FAILURE);
	}

	std::ostringstream situatedControllerStream;
	situatedControllerStream << envID << FIELD_SEPARATOR << envDesc << FIELD_SEPARATOR << contrDesc;
	return situatedControllerStream.str();
}

#endif // EVCLIB_SITUATED_CONTROLLER_H
