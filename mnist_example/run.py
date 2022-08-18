from slurm_launcher.sbatch_launcher import launch_tasks


def sample_run():
    PYTHON_FILE = "python ./main.py" # do not include 'python' in your file name
    PARAM_DICT = {
        "--lr" : [1, 0.5, 0.25, 0.1, 0.05, 0.025, 0.01],
        }

    PART_TO_PY = {
        'dept' : '~/anaconda3/envs/SAC/bin/python', #python
        'titan' : '~/anaconda3/envs/SAC/bin/python', #python
        'rtx2080' : '~/anaconda3/envs/SAC/bin/python', #python
        'rtx3090' : '~/anaconda3/envs/SAC3090/bin/python', #python
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