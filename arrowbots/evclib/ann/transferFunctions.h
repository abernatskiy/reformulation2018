#ifndef TRANSFER_FUNCTIONS_H
#define TRANSFER_FUNCTIONS_H

#include <cmath>

template<class RealNumber> RealNumber logistic(RealNumber in)
{
	return (RealNumber) (1./(1.+exp(-1.*((double) in))));
}

template<class RealNumber> RealNumber tanHyperbolic(RealNumber in)
{
	return (RealNumber) tanh((double) in);
}

#endif // TRANSFER_FUNCTIONS_H
