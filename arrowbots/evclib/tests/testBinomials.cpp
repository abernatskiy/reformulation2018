#include <iostream>
#include "../misc.h"

int main(int argc, char** argv)
{
	int p = 100;
	for(int i=0; i<=p; i++)
		std::cout << binomialCoeff(p, i) << std::endl;
	return 0;
}
