#!/bin/bash

args=("$@")
bash -c "${args[$SLURM_PROCID]}"
