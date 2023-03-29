import os
import itertools
import time
import signal
import subprocess
import filelock
import pathlib
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
        print("Already %s exists" % dirname)

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

def launch_tasks(
        param_option: int,
        base_cmd: str,
        param_dict: dict,
        partition: str='dept,titan,rtx2080,rtx3090,a100',
        exclude: str=None,
        qos: str='normal',
        timeout: str='INFINITE',
        job_name: str=None,
        max_job_num: int=40,
        return_after_finish: bool=False,
        part_to_py: dict=None,
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
    nkey = len(param_keys)
    param_list = [
        v for v in itertools.product(
            *tuple([param_dict[key] for key in param_keys]))
    ]

    path = pathlib.Path(__file__).parent.resolve()
    file = open("{}/config.py".format(path), "w+")
    file.write("PARTITION2PYTHON = {\n")
    if part_to_py is not None:
        for part, env in part_to_py.items():
            file.write("    '{}' : '{}',\n".format(part, env))
    else:
        for part in ['dept', 'titan', 'rtx2080', 'rtx3090', 'a100']:
            file.write("    '{}' : 'python',\n".format(part))
    file.write("}\n")
    file.close()

    file = open("{}/config.py".format(path), "r")
    print("print config.py contents")
    print(file.read())
    file.close()

    if job_name is not None:
        create_dir('./slurm/{}'.format(job_name))
    else:
        create_dir('./slurm')

    sbatch_cmds = []
    for i in range(0, len(param_list), nprocs):
        cmd_pair = ""
        for j in range(nprocs):
            if (i + j >= len(param_list)):
                break
            param = param_list[i + j]
            cmd = 'python {}/select_env_wrap.py "{}"'.format(path, base_cmd) + ' ' + ''.join([
                '{} {} '.format(param_keys[key_idx], param[key_idx])
                for key_idx in range(nkey)
            ])
            cmd_pair += "'{}'".format(cmd) + " "
        sbatch_cmd = "sbatch --partition={} --qos={} --time={} --ntasks={} --cpus-per-task={} --mem={} --gres=gpu:{}".format(
            partition, qos, timeout, nprocs, cpus, mem, gpus)

        if exclude is not None:
            sbatch_cmd += ' --exclude {}'.format(exclude)

        if job_name is not None:
            sbatch_cmd += " --job-name={} --output ./slurm/{}/%j.out".format(
                job_name, job_name)
        else:
            sbatch_cmd += " --output ./slurm/%j.out"

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

