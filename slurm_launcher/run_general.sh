#!/bin/bash

#SBATCH --nodes 1

srun hostname
a=''
while (( "$#" )); do
  a="$a '$1'"
  shift
done
srun bash -c "run_general_supp.sh $a"

