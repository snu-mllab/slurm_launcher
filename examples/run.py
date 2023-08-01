from slurm_launcher.sbatch_launcher import launch_tasks

def sample_run():
    PYTHON_FILE = "python ./main.py" # do not include 'python' in your file name
    PYTHON_BIN = '~/anaconda3/bin/python'
    PARAM_DICT = {
        "--seed" : [0, 1, 2, 3, 4],
        # "--lr": [1e-1, 1e-2, 1e-3, 1e-4],
        # "--batch_size": [64, 128, 256],
        }

    PART_TO_PY = {
        'dept' : PYTHON_BIN,
        'titan' : PYTHON_BIN,
        'rtx2080' : PYTHON_BIN,
        'rtx3090' : PYTHON_BIN,
        'a100' : PYTHON_BIN,
        'cpu' : PYTHON_BIN,
        'deepmetrics' : PYTHON_BIN,
    }
    
    '''
    the last parameter of launch_tasks is optional.
    use default value to use the python of the
    activated environment when you launch the job.
    '''

    launch_tasks(
        param_option=1,
        base_cmd=PYTHON_FILE,
        param_dict=PARAM_DICT,
        partition='rtx3090',
        qos='normal',
        timeout='7-0',
        job_name='sample',
        part_to_py=PART_TO_PY,
    ) 

if __name__=='__main__':
    sample_run()