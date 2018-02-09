#PBS -l nodes=1:ppn=1
#PBS -l walltime=00:10:00
#PBS -N myjob
#PBS -j oe
#PBS -m bea

cd $PBS_O_WORKDIR
echo "This is myjob running on " `hostname`
/users/a/b/abernats/anaconda/bin/python2.7 /users/a/b/abernats/evscripts/parallelQ.py $PBS_ARRAYID
