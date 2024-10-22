#!/bin/bash -l
#SBATCH --partition=week
#SBATCH -N 2
#SBATCH --time=7-0:00                  #Time limit for this job
#SBATCH --ntasks-per-node=40               #Number of CPU's Per node
#SBATCH --job-name=test         #Name of this job in work queue
#SBATCH --mail-user=monsiar0182@uwec.edu   #Email to send notifications to
#SBATCH --mail-type=ALL                   #Email notification type (BEGIN, END, FAIL, ALL)

export PYTHONUNBUFFERED=TRUE
module load parallel

coeffarr=(0.05 0.1 0.15 0.2 0.25 0.3 0.35 0.4 0.45 0.5 0.55 0.6 0.65 0.7 0.75 0.8 0.85 0.9 0.95)
srun="srun --exclusive -N1 -n1 --cpus-per-task=4"
parallel="parallel --delay 0.2 -j 20 --joblog ./trainlogs/jobs.log --resume"
$parallel "$srun ./scripts/prescribe_model.sh {1}" ::: "${coeffarr[@]}"

cd ../../../../

python ./prescriptor_robojudge.py
