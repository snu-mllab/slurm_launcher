import os
import sys
import socket

from slurm_launcher.partition_info import DEPTNodes, TITANNodes, RTX2080Nodes, RTX3090Nodes, A100Nodes, DEEPMETRICSNodes
from slurm_launcher.config import PARTITION2PYTHON

script = sys.argv[1]

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
elif hostname in DEEPMETRICSNodes:
    partition = 'deepmetrics'
else:
    print("Uncovered hostname({})".format(hostname))

if partition in PARTITION2PYTHON.keys():
    script = script.replace("python", PARTITION2PYTHON[partition])
script = script + ' ' + ' '.join(sys.argv[2:])

print("hostname : {}, partition : {}, script : {}".format(hostname, partition, script), flush=True)
os.system(script)
