import itertools
import os
from platform import python_version
import signal
import subprocess
import filelock
import pathlib
from slurm_launcher.sbatch_params import get_sbatch_params


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


def launch_tasks(
        param_option: int,
        base_cmd: str,
        param_dict: dict,
        partition: str='dept,titan,rtx2080,rtx3090',
        exclude: str='',
        qos: str='normal',
        timeout: str='48:00:00',
        job_name: str=None,
        part_to_py: dict=None,
    ):
    """
    Launch slurm jobs
    """
    lock = filelock.FileLock("/etc/slurm/slurm_lock")
    lock.acquire()
    try:
        os.system('update_slurm_node_weight.sh')
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
            for part in ['dept', 'titan', 'rtx2080', 'rtx3090']:
                file.write("    '{}' : 'python',\n".format(part))
        file.write("}\n")

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
            if exclude is not '':
                sbatch_cmd += ' --exclude {}'.format(exclude)
            if job_name is not None:
                create_dir('./slurm/{}'.format(job_name))
                sbatch_cmd += " --job-name={} --output ./slurm/{}/%j.out".format(
                    job_name, job_name)
            else:
                create_dir('./slurm')
                sbatch_cmd += " --output ./slurm/%j.out"

            sbatch_cmd += " run_general.sh {}".format(cmd_pair)
            print(sbatch_cmd)
            subprocess.check_call(sbatch_cmd, shell=True)
    finally:
        lock.release()


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

