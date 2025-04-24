python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# let's install scip.

# we need conda
https://www.anaconda.com/docs/getting-started/anaconda/install
(ideally: ship conda, forward license reqs)

PATH=$PATH:~/anaconda3/bin/

https://github.com/conda-forge/scipoptsuite-feedstock:
conda config --add channels conda-forge
conda config --set channel_priority strict



ummm.. or https://github.com/scipopt/PySCIPOpt


I had to do this
sudo apt-get install python3-tk

