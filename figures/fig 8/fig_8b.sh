#!/bin/bash

MORPHOLOGYTYPE="integerVectorRandomJumps"

cp ../rateSwipe_N3/error_vs_probabilityOfMutatingClass0_at_compositeClass0${MORPHOLOGYTYPE}.png ./tile_r0_c0.png
cp ../rateSwipe_N3/mmmmd_vs_probabilityOfMutatingClass0_at_compositeClass0${MORPHOLOGYTYPE}.png ./tile_r1_c0.png
cp ../rateSwipe_N5/error_vs_probabilityOfMutatingClass0_at_compositeClass0${MORPHOLOGYTYPE}.png ./tile_r0_c1.png
cp ../rateSwipe_N5/mmmmd_vs_probabilityOfMutatingClass0_at_compositeClass0${MORPHOLOGYTYPE}.png ./tile_r1_c1.png
cp ../rateSwipe_N10/error_vs_probabilityOfMutatingClass0_at_compositeClass0${MORPHOLOGYTYPE}.png ./tile_r0_c2.png
cp ../rateSwipe_N10/mmmmd_vs_probabilityOfMutatingClass0_at_compositeClass0${MORPHOLOGYTYPE}.png ./tile_r1_c2.png

montage -border 0 -geometry 1920x -tile 3x2 tile* fig_4b.png
