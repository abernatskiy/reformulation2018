# reformulation2018

Materials required to reproduce "Evolving Morphology Automatically Reformulates The Problem Of Designing Modular Control"

To run this code you will need a Portable Batch System cluster capable of supporting at least 400 processes (less if you don't run the scripts that involve 10-segment arrowbots).

Steps:

1. Compile the simulator:

```bash
$ cd arrowbots/
$ make
$ cd ..
```

2. Configure the parameters of your cluster:

> $ nano pbsGridWalker/environment/host/vacc.py

3. Run the parametric swipe scripts on the cluster's root node:

```bash
$ ./pbsGridWalker/pgw_experiment.py ./simpleTimeSeries.py
$ ./pbsGridWalker/pgw_experiment.py ./simpleTimeSeries5.py
$ ./pbsGridWalker/pgw_experiment.py ./simpleTimeSeries10.py
$ ./pbsGridWalker/pgw_experiment.py ./autoscripts/ccSwipe_N3.py
$ ./pbsGridWalker/pgw_experiment.py ./autoscripts/ccSwipe_N5.py
$ ./pbsGridWalker/pgw_experiment.py ./autoscripts/ccSwipe_N10.py
$ ./pbsGridWalker/pgw_experiment.py ./autoscripts/rateSwipe_N3.py
$ ./pbsGridWalker/pgw_experiment.py ./autoscripts/rateSwipe_N5.py
$ ./pbsGridWalker/pgw_experiment.py ./autoscripts/rateSwipe_N10.py
```

This should produce nine folders with the same names as the scripts that produced them. Within each of these folders there will be a "results" subfolder with panels of the figures from the paper.

If something goes wrong, it is a good idea to check if paths to the system binaries are configured correctly:

```bash
$ nano pbsGridWalker/environment/os/gentoo.py
```

Vector files for hand-drawn illustrations and some useful scripts for combining the panels are located at ./figures.
