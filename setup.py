from distutils.core import setup
from setuptools import find_packages

setup(
    name='slurm_launcher',
    version='0.1.0',
    packages=find_packages(),
    license='MIT',
    description='A library for launching slurm jobs',
    scripts=['slurm_launcher/run_general.sh', 'slurm_launcher/run_general_supp.sh']
)
