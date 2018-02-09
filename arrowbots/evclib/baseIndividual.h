/* Base class for individuals/phenotypes,
   designed for compatibility with evalQueue
   template.

   For full compartibility, ensure additionally
   that a Hyperparameters type is defined and
   that the chuld class can be constructed out
   of it.
 */

#ifndef EVCLIB_BASE_INDIVIDUAL_H
#define EVCLIB_BASE_INDIVIDUAL_H

#include <string>

class BaseIndividual
{
private:
	double eval;
protected:
	int id;
public:
	BaseIndividual() : eval(-1.) {};
	double getEvaluation() {return eval;};
	void setEvaluation(double e) {eval = e;};
	int getID() {return id;};

	virtual void getParameters(std::string) = 0;
	virtual std::string getDesc() const = 0;
};

#endif // EVCLIB_BASE_INDIVIDUAL_H
