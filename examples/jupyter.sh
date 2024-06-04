#!/bin/bash

#SBATCH --partition cpu,dept,titan,rtx2080,rtx3090

#SBATCH --nodes 1

#SBATCH --ntasks 1

#SBATCH --cpus-per-task 10

#SBATCH --gres gpu:0

#SBATCH --time UNLIMITED

#SBATCH --job-name jupyter

#SBATCH --mem 60000

#SBATCH --qos normal

unset XDG_RUNTIME_DIR

date;pwd

host=$(hostname)
ip=$(ifconfig | grep 147 | awk '{print $2}')
port=$(ruby -e 'require "socket"; puts Addrinfo.tcp("", 0).bind {|s| s.local_address.ip_port }')
echo ${host}
echo ${ip}
echo ${port}

jupyter-lab --ip=${ip} --port=${port} --no-browser
