#!/bin/bash -l

# Batch script to run a serial job under SGE.

# Request 24 hours of wallclock time (format hours:minutes:seconds).
#$ -l h_rt=24:00:0

# Request 1 terabyte of RAM (must be an integer followed by M, G, or T)
#$ -l mem=100G

# Request 1 GPU for the job
#$ -l gpu=1

# request a V100 node only, the line below says EF because only E-type and F-type nodes has nVidia Tesla V100s
#$ -ac allow=EF

# Request 15 gigabyte of TMPDIR space (default is 10 GB - remove if cluster is diskless)
#$ -l tmpfs=15G

# Set the name of the job.
#$ -N LSTM_old

# Set the working directory to somewhere in your scratch space.  
#  This is a necessary step as compute nodes cannot write to $HOME.
# Replace "<your_UCL_id>" with your UCL user ID.
# the jobscript output and error files will be here
#$ -wd /home/zceesko/Scratch/script_outputs

# Your work should be done in $TMPDIR 
cd ../MEng-V2I

# Modules to load for the non-MKL GPU version of tensorflow
module unload compilers mpi
module load compilers/gnu/4.9.2
module load python3/recommended
module load cuda/10.1.243/gnu-4.9.2
module load cudnn/7.6.5.32/cuda-10.1
module load tensorflow/1.14.0/gpu
# install torch on my directory
pip3 install --user torch==1.7.1+cu101 torchvision==0.8.2+cu101 torchaudio==0.7.2 -f https://download.pytorch.org/whl/torch_stable.html

# Run the application and put the output into a file called SARIMA.txt, placed in the current directory, after any cd
/usr/bin/time --verbose python3 TimeSeriesPrediction/main.py --network 'lstm' --transfer_learning True --mode 'train' > LSTM_old.txt

# Preferably, tar-up (archive) all output files onto the shared scratch area
# the $TMPDIR at the end means that the tar file is compressing the TMPDIR folder for that job
tar -zcvf $HOME/Scratch/script_outputs/files_from_job_$JOB_ID.tar.gz $TMPDIR

# Make sure you have given enough time for the copy to complete!