#PBS -l nodes=1:ppn=1
#PBS -N experimentJob
#PBS -j n
#PBS -m a

cd $PBS_O_WORKDIR
echo "This is pbs.sh running on `hostname`"
echo  "Starting a worker with command line $PYTHON ${PBSGRIDWALKER_HOME}/worker.py $PARENT_SCRIPT $POINTS_PER_JOB"
$PYTHON ${PBSGRIDWALKER_HOME}/worker.py $PARENT_SCRIPT $POINTS_PER_JOB
