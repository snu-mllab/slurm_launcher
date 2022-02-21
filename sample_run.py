from slurm_launcher.sbatch_launcher import launch_tasks


def sample_run():
    PYTHON_FILE = "python ./some_file.py" # do not include 'python' in your file name
    PARAM_DICT = {
        "--seed" : [0, 1, 2, 3, 4],
        # "--lr": [1e-1, 1e-2, 1e-3, 1e-4],
        # "--batch_size": [64, 128, 256],
        }

    launch_tasks(
        param_option=1,
        base_cmd=PYTHON_FILE,
        param_dict=PARAM_DICT,
        partition='dept,titan,rtx2080',
        exclude='',
        qos='normal',
        timeout='INFINITE',
        job_name='sample',
    ) 

if __name__=='__main__':
    sample_run()