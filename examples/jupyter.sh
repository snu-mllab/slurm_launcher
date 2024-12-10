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
port=$(/usr/bin/python3 -c "import socket;sock=socket.socket();sock.bind(('', 0));print(sock.getsockname()[1])")
ip=$(/usr/bin/python3 -c "import socket; print([l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith(\"127.\")][:1], [[(s.connect((\"8.8.8.8\", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0])")

echo ${host}
echo ${ip}
echo ${port}

jupyter-lab --ip=${ip} --port=${port} --no-browser
