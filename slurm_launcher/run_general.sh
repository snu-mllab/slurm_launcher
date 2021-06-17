#!/bin/bash

#SBATCH --nodes 1

srun hostname
a=''
while (( "$#" )); do
  a="$a '$1'"
  shift
done
srun bash -c "/home/seungyong/slurm_tutorial_v10/run_general_supp.sh $a"

