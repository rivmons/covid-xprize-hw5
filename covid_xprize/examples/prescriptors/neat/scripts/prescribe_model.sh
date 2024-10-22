#!/usr/bin/bash

# python train_prescriptor.py -coeff $1 >> trainlogs/train_${1}.log

# mv ./${1}-neat-checkpoint-* checkpoints/
python3 prescribe.py --start_date 2020-08-01 --end_date 2020-08-05 -ip ../../../oxford_data/data/OxCGRT_latest.csv -o prescriptions/test_prescriptions_${1}.csv -c ./cost_geo.csv -coeff ${1}
