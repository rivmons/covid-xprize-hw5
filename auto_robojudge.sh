#!/bin/bash -l
#SBATCH --partition=week
##SBATCH -N 1 
#SBATCH --time=7-0:00                  #Time limit for this job
#SBATCH --ntasks-per-node=64               #Number of CPU's Per node
#SBATCH --job-name=test         #Name of this job in work queue
#SBATCH --mail-user=monsiar0182@uwec.edu   #Email to send notifications to
#SBATCH --mail-type=ALL                   #Email notification type (BEGIN, END, FAIL, ALL)

# coeffarr=(0.3 0.35 0.4 0.45 0.5 0.55 0.6 0.65 0.7 0.75 0.8 0.85 0.9 0.95 0.05 0.1 0.15 0.2 0.25)
# chkpt=(14 15 16 17 18 19)
# for c in "${coeffarr[@]}"
# do
#     for pt in "${chkpt[@]}"
#     do
#         python ./prescriptor_robojudge.py -coeff $c -checkpoint $pt
#     done
# done

export PYTHONUNBUFFERED=TRUE

python ./prescriptor_robojudge.py