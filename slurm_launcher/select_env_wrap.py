import os
import sys
import socket
import json
import pathlib

from slurm_launcher.partition_info import DEPTNodes, TITANNodes, RTX2080Nodes, \
    RTX3090Nodes, A100Nodes, RTX6000ANodes, CPUNodes, DEEPMETRICSNodes

job_name = sys.argv[1]
script = sys.argv[2]

hostname = str(socket.gethostname())
partition = ''

if hostname in DEPTNodes: 
    partition = 'dept'
elif hostname in TITANNodes:
    partition = 'titan'
elif hostname in RTX2080Nodes:
    partition = 'rtx2080'
elif hostname in RTX3090Nodes:
    partition = 'rtx3090'
elif hostname in A100Nodes:
    partition = 'a100'
elif hostname in RTX6000ANodes:
    partition = 'rtx6000a'
elif hostname in CPUNodes:
    partition = 'cpu'
elif hostname in DEEPMETRICSNodes:
    partition = 'deepmetrics'
else:
    print("Uncovered hostname({})".format(hostname))

path = pathlib.Path(__file__).parent.resolve()
config_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "configs",
                            f"config_{job_name}.json")
with open(config_path, 'r') as f:
    part_to_py = json.load(f)

if partition in part_to_py.keys():
    script = script.replace("python", part_to_py[partition], 1)
script = script + ' ' + ' '.join(sys.argv[3:])

print("hostname : {}, partition : {}, script : {}".format(hostname, partition, script), flush=True)
os.system(script)
