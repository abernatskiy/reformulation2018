/* Generic Phenotype class for vectors of numbers.
   Compatible with EvalQueue template.

   Constructs from an instance of empty class for
   compatibility. Empty class
   NumericVectorHyperparameters is provided for
   convenience.

   Can read parameters from string of the
   following format:

   ID val0 val1 ... valN-1

   where:

     ID is the ID of the phenotype.

     val0 to valN-1 are numeric text fields describing
       phenotype/individual. The number of fields N is
       determined automatically.

     ' ' is the field separator defined by the
       FIELD_SEPARATOR define directive.
*/

#ifndef EVCLIB_NUMERIC_VECTOR_H
#define EVCLIB_NUMERIC_VECTOR_H

#include <string>
#include <sstream>
#include <vector>
#include <iostream>

#include "baseIndividual.h"

#ifndef FIELD_SEPARATOR
#define FIELD_SEPARATOR ' '
#endif // FIELD_SEPARATOR

class NumericVectorHyperparameters {};

template<typename NumericType>
class NumericVector : public BaseIndividual
{
public:
	std::vector<NumericType> vals; // publishing to simplify the use in unusual genotype to phenotype maps (see e.g. Arrowbot)
	NumericVector() : BaseIndividual() {};
	NumericVector(const NumericVectorHyperparameters&) : BaseIndividual() {}; // required for compatibility with EvalQueue

	void getParameters(std::string);
	std::string getDesc() const;
};

// DEFINITIONS

template<class NumericType>
void NumericVector<NumericType>::getParameters(std::string genotype)
{
	// separate the full genotype into strings for ID and numeric text fields
	std::stringstream ss(genotype);

	std::string textField;
	std::getline(ss, textField, FIELD_SEPARATOR);
	id = std::stoi(textField);

	while(std::getline(ss, textField, FIELD_SEPARATOR) && textField.length())
		vals.push_back(static_cast<NumericType>(std::stod(textField)));

	setEvaluation(-1.);
}

template<class NumericType>
std::string NumericVector<NumericType>::getDesc() const
{
	std::ostringstream ss;
	ss << id;
	for(auto it=vals.begin(); it!=vals.end(); it++)
		ss << FIELD_SEPARATOR << *it;
	return ss.str();
}

#endif // EVCLIB_NUMERIC_VECTOR_H
