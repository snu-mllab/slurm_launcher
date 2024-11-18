import os
import itertools
import time
import signal
import subprocess
import filelock
import pathlib
import json
from typing import Dict
from slurm_launcher.sbatch_params import get_sbatch_params
from slurm_launcher.partition_info import *

lock = filelock.FileLock("/etc/slurm/slurm_lock")

def create_dir(dirname: str):
    """
    Create directory named dirname
    """
    if not os.path.exists(dirname):
        print("Creating %s" % dirname)
        try:
            os.makedirs(dirname)
        except FileExistsError:
            pass
    else:
        print("%s already exists" % dirname)

def count_job(job_name, username, concatenator="!"):
    target_string = username + concatenator + job_name
    squeue = subprocess.check_output(['squeue', '-o', f'%u{concatenator}%j']).decode('utf-8').strip()
    return squeue.count(target_string)

def wait_finish(job_name, username, concatenator="!"):
    """
    To use this function, your user name and job name should not contain "!" character
    If not, use the character which is not used in your user name and job name as a concatenator
    """
    while True:
        if count_job(job_name, username, concatenator) == 0:
            break
        else:
            time.sleep(60)

def join_params_by_style(param_keys: Dict[int, str], param: Dict[int, str], style: str):
    if style == "argparse":
        return ' '.join(['{} {}'.format(param_keys[key_idx], param[key_idx])
            for key_idx in range(len(param_keys))])
    elif style == "hydra":
        return ' '.join(['{}={}'.format(param_keys[key_idx].lstrip("--"), param[key_idx])
            for key_idx in range(len(param_keys))])
    else:
        raise NotImplementedError(f"style {style} is not supported")

def launch_tasks(
        param_option: int,
        base_cmd: str,
        param_dict: dict,
        partition: str='dept,titan,rtx2080,rtx3090,a100,ada',
        exclude: str=None,
        qos: str='normal',
        timeout: str='7-0',
        job_name: str=None,
        max_job_num: int=40,
        return_after_finish: bool=False,
        part_to_py: dict=None,
        args_style: str="argparse",
    ):
    """
    Launch slurm jobs
    mode: 'gather' or 'spread'
    """
    username = os.environ['USER']

    sbp_dict = get_sbatch_params(param_option)
    nprocs = sbp_dict['nprocs']
    cpus = sbp_dict['cpus']
    mem = sbp_dict['mem']
    gpus = sbp_dict['gpus']

    param_keys = [str(v) for v in param_dict.keys()]
    param_list = [
        v for v in itertools.product(
            *tuple([param_dict[key] for key in param_keys]))
    ]

    path = pathlib.Path(__file__).parent.resolve()
    if part_to_py is None:
        part_to_py = {part: "python" for part in partition.split(',')}
    config_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "configs",
                               f"config_{job_name}.json")
    with open(config_path, 'w') as f:
        json.dump(part_to_py, f)

    log_dir = "./slurm"
    if job_name is not None:
        log_dir = os.path.join(log_dir, job_name) 
    create_dir(log_dir)

    sbatch_cmds = []
    for i in range(0, len(param_list), nprocs):
        cmd_pair = ""
        for j in range(nprocs):
            if (i + j >= len(param_list)):
                break
            param = param_list[i + j]
            cmd = 'python {}/select_env_wrap.py "{}" "{}"'.format(path, job_name, base_cmd) + ' '
            cmd += join_params_by_style(param_keys, param, args_style)
            cmd_pair += "'{}'".format(cmd) + " "
        sbatch_cmd = "sbatch --partition={} --qos={} --time={} --ntasks={} --cpus-per-task={} --mem={} --gres=gpu:{}".format(
            partition, qos, timeout, nprocs, cpus, mem, gpus)

        if exclude is not None:
            sbatch_cmd += ' --exclude {}'.format(exclude)

        if job_name is not None:
            sbatch_cmd += " --job-name={} --output {}/%j.out".format(
                job_name, log_dir)
        else:
            sbatch_cmd += " --output {}/%j.out".format(log_dir)

        sbatch_cmd += " run_general.sh {}".format(cmd_pair)
        sbatch_cmds.append(sbatch_cmd)

    print(f"Total {len(sbatch_cmds)} jobs to be submitted...")

    while sbatch_cmds:
        if count_job(job_name, username) >= max_job_num:
            time.sleep(60)
            continue
        else:
            with lock:
                os.system('update_slurm_node_weight.sh')
                left_job_num = len(sbatch_cmds)
                left_slot_num = max_job_num - count_job(job_name, username)

                for i in range(min(left_job_num, left_slot_num)):
                    sbatch_cmd = sbatch_cmds.pop(0)
                    print(sbatch_cmd)
                    subprocess.check_call(sbatch_cmd, shell=True)


    if return_after_finish:
        wait_finish(job_name, username)


def srun_gpuless_task(cmd,
                      cpus=2,
                      mem=6000,
                      partition='dept,titan',
                      qos='normal',
                      timeout='12:00:00',
                      job_name=None):
    srun_cmd = "srun --partition={} --qos={} --time={} --ntasks=1 --cpus-per-task={} --mem={}".format(
            partition, qos, timeout, cpus, mem)
    if job_name is not None:
        srun_cmd += " --job-name={}".format(job_name)
    srun_cmd += ' ' + cmd
    print(srun_cmd)
    p = subprocess.Popen(srun_cmd, shell=True)
    srun_pid = p.pid
    def handler(signum, frame):
        os.kill(srun_pid, signum)
    signal.signal(signal.SIGINT, handler)
    p.wait()

