CC=g++
#CFLAGS=-std=c++11 -O2 -msse2 -ffast-math -m64 -fno-rtti -fno-exceptions -fno-stack-protector ${MORECFLAGS} -g -ggdb -Wall -DDEBUG=true
CFLAGS=-std=c++11 -O2 -msse2 -ffast-math -m64 -fno-exceptions -fno-stack-protector ${MORECFLAGS} -g -ggdb -Wall -DNDEBUG -DBOOST_UBLAS_NDEBUG
LDFLAGS=-m64 -g -ggdb -Wall
OBJECTS=main.o arrowbotSimulator.o evclib/ann/direct.o inih/cpp/INIReader.o inih/ini.o

all: arrowbotEvaluator

arrowbotEvaluator : $(OBJECTS)
	$(CC) -o $@ $^ $(LDFLAGS)

##########################################
# Generic rules
##########################################

%.o: %.cpp %.h
	$(CC) -o $@ -c $< $(CFLAGS)

%.o: %.cpp
	$(CC) -o $@ -c $< $(CFLAGS)

clean:
	rm -f ${OBJECTS} arrowbotEvaluator
