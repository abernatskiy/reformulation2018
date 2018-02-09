#!/bin/bash
mkdir finalFitnesses
for seg in 3 5 10; do for morphology in identity null; do for method in sparse random; do cut -d ' ' -f 501 ./twoMorphologies_N${seg}/results/SA${morphology}_IP${method}_fitness > finalFitnesses/seg${seg}_morpology${morphology}_method${method} ; done; done; done
