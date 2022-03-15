from slurm_launcher.sbatch_launcher import launch_tasks


def sample_run():
    PYTHON_FILE = "python ./main.py" # do not include 'python' in your file name
    PARAM_DICT = {
        "--seed" : [0, 1, 2, 3, 4],
        # "--lr": [1e-1, 1e-2, 1e-3, 1e-4],
        # "--batch_size": [64, 128, 256],
        }

    PART_TO_PY = {
        'dept' : '~/anaconda3/envs/pt1/bin/python', #python
        'titan' : '~/anaconda3/envs/pt2/bin/python', #python
        'rtx2080' : '~/anaconda3/envs/pt3/bin/python', #python
        'rtx3090' : '~/anaconda3/envs/pt4/bin/python', #python
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
        exclude='',
        qos='normal',
        timeout='INFINITE',
        job_name='sample',
        part_to_py=PART_TO_PY,
    ) 

if __name__=='__main__':
    sample_run()