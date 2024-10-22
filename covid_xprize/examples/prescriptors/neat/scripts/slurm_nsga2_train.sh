#!/bin/bash -l
#SBATCH --partition=week
##SBATCH -N 1
#SBATCH --time=7-0:00                  #Time limit for this job
#SBATCH --ntasks-per-node=64               #Number of CPU's Per node
#SBATCH --job-name=testnsga2         #Name of this job in work queue
#SBATCH --mail-user=monsiar0182@uwec.edu   #Email to send notifications to
#SBATCH --mail-type=ALL                   #Email notification type (BEGIN, END, FAIL, ALL)

export PYTHONUNBUFFERED=TRUE

# python train_prescriptor_nsga2.py -coeff 0.5
# mv nsga2-neat-* nsga2/

python3 prescribe.py --start_date 2020-08-01 --end_date 2020-08-05 -ip ../../../oxford_data/data/OxCGRT_latest.csv -o nsga2/test_prescriptions_nsga2.csv -c ./cost_geo.csv -coeff 0
cd ../../../../
python3 prescriptor_robojudge.py