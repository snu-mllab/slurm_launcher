import os
import sys
import argparse
import pwd
import socket

from config import DEPTNodes, TITANNodes, RTXNodes, RTX3090Nodes, PARTITION2PYTHON

script = sys.argv[1]

hostname = str(socket.gethostname())
partition = ''

if hostname in DEPTNodes: 
    partition = 'dept'
elif hostname in TITANNodes:
    partition = 'titan'
elif hostname in RTXNodes:
    partition = 'rtx2080'
elif hostname in RTX3090Nodes:
    partition = 'rtx3090'
else:
    print("Uncovered hostname({})".format(hostname))

if partition in PARTITION2PYTHON.keys():
    script = script.replace("python", f"{PARTITION2PYTHON[partition]}")
script = script +' '+ ' '.join(sys.argv[2:])

print("hostname : {}, partition : {}, script : {}".format(hostname, partition, script))
os.system(script)
