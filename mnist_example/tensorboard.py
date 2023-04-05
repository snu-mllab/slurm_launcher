from tensorboardX import SummaryWriter
from slurm_launcher.sbatch_launcher import srun_gpuless_task
import os 

class SummaryWriterManager:
    def __init__(self, path):
        if not os.path.exists(path): os.makedirs(path) 
        self.writer = SummaryWriter(path)
        
    def add_summary(self, tag, value, global_step):
        self.writer.add_scalar(tag=tag, scalar_value=value, global_step=global_step)

    def add_summaries(self, dict_, global_step):
        for key in dict_.keys():
            self.add_summary(tag=str(key), value=dict_[key], global_step=global_step)

def run_tensorboard():
    TENSORBOARD_DIR = "./board"
    srun_gpuless_task(
            cmd=r"""bash -c 'tensorboard --host=$(hostname).mllab.snu.ac.kr --port=0 --logdir={}'""".format(TENSORBOARD_DIR),
            partition='cpu,dept,titan,rtx2080,rtx3090',
            job_name='tensorboard',
    )

if __name__ == "__main__":
    run_tensorboard()