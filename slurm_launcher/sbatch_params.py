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
        cpus=20
        mem=180000
        gpus=3
    elif gpu_options==4:
        nprocs=1
        cpus=20
        mem=240000
        gpus=4
    elif gpu_options==12:
        nprocs=2
        cpus=4
        mem=60000
        gpus=1
    elif gpu_options==13:
        nprocs=3
        cpus=2
        mem=60000
        gpus=1
    elif gpu_options==14:
        nprocs=4
        cpus=2
        mem=60000
        gpus=1
    else:
        print("Invalid option")
        exit(0)
    return dict(nprocs=nprocs, cpus=cpus, mem=mem, gpus=gpus)

