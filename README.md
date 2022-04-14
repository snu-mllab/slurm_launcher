# Slurm Launcher
A Python library for launching Slurm tasks

## How to install
```
git clone https://github.com/snu-mllab/slurm_launcher
cd slurm_launcher
pip install -e .
```

## Example
Please refer to `examples/run.py`.
```
cd examples
python run.py
```

## MNIST example & Tensorboard tutorial
* Installation of tensorboard
```
pip install tensorboardX
pip install tensorboard
```

* Run MNIST training
```
cd mnist_example
python main.py
```

* Run tensorboard
```
python tensorboard.py
```