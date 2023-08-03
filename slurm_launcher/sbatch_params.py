def get_sbatch_params(gpu_options):
    if gpu_options==1:
        nprocs=1
        cpus=10
        mem=60000
        gpus=1
    elif gpu_options==2:
        nprocs=1
        cpus=20
        mem=120000
        gpus=2
    elif gpu_options==3:
        nprocs=1
        cpus=30
        mem=180000
        gpus=3
    elif gpu_options==4:
        nprocs=1
        cpus=45
        mem=240000
        gpus=4
    elif gpu_options==8:
        nprocs=1
        cpus=90
        mem=480000
        gpus=8
    elif gpu_options==21:
        nprocs=2
        cpus=5
        mem=60000
        gpus=1
    elif gpu_options==31:
        nprocs=3
        cpus=3
        mem=60000
        gpus=1
    elif gpu_options==41:
        nprocs=4
        cpus=2
        mem=60000
        gpus=1
    elif gpu_options==51:
        nprocs=5
        cpus=2
        mem=60000
        gpus=1
    elif gpu_options==10:
        nprocs=1
        cpus=1
        mem=6000
        gpus=0
    elif gpu_options==20:
        nprocs=1
        cpus=2
        mem=12000
        gpus=0
    elif gpu_options==450:
        nprocs=1
        cpus=45
        mem=240000
        gpus=0
    elif gpu_options==600:
        nprocs=1
        cpus=60
        mem=480000
        gpus=0
    elif gpu_options==900:
        nprocs=1
        cpus=90
        mem=480000
        gpus=0
    elif gpu_options==1200:
        nprocs=1
        cpus=120
        mem=480000
        gpus=0
    else:
        print("Invalid option")
        exit(0)
    return dict(nprocs=nprocs, cpus=cpus, mem=mem, gpus=gpus)

