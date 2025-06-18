Gurobi is no longer supported (because I don't have a license anymore) and the gcc-with-python plugin flow is getting replaced by an LLVM pass.  
Here are some legacy notes:  

<a name="installing_gurobi"></a>
## Installing Gurobi

You will need Gurobi (latest version available for academic use)-- please download it from gurobi.com, where you can also get an [academic license](https://www.gurobi.com/academia/academic-program-and-licenses/).  You must be connected to your institution's network (VPN or on-prem).

```
cd ~/Downloads
#replace x with gurobi version
tar -xzf gurobix_linux64.tar.gz
```

Managing your permissions carefully, copy the untarred folder to a folder like `/opt/`.
Follow the instruction on Gurobi's website (such as running grbgetkey to activate your license).

You can add the following to your ~/.bashrc (feel free to add
the equivalent for other shells)

```
# gurobi
#set appropriate gurobi folder name based on your gurobi version
export GUROBI_HOME="/opt/gurobi902/linux64"
export PATH="$PATH:/opt/gurobi902/linux64/bin/"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:${GUROBI_HOME}/lib"
```
In `/opt/gurobi902/linux64`, run

```
python3 setup.py install --user
```

If
```
python3 -c "import gurobipy"
```
 doesn't throw an error, you're good to go.


Now that Gurobi is installed, on to other dependencies!

## Other dependencies

### Ubuntu 18.04.1 LTS, valid as of Feb 11 2021

Run the following
```
sudo apt update
sudo apt install python3-pip python3-pil.imagetk dot2tex zsh gcc-9-plugin-dev jq

# Please use python3 (3.6 and above, we use fstrings)
pip3 install -r requirements.txt
```


## GCC Plugin Setup

Use the following command to add gcc python plugin:
```bash
git submodule add ist-git@git.uwaterloo.ca:watcag-public/gcc-python-plugin.git src/gcc-python-plugin
```
gcc-python-plugin must be built with python3.5

use the following commands to setup
```
#WORKDIR refers to your working folder, which includes this repository
export CGRA_ILP_PATH=~/WORKDIR/cgra-ilp
export GCC_PLUGIN_PATH=$CGRA_ILP_PATH/src/gcc-python-plugin
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$GCC_PLUGIN_PATH:$GCC_PLUGIN_PATH/gcc-c-api
export PATH="$PATH:/usr/local/etc/cmake-3.15.5-Linux-x86_64/bin"
```

Must install `sudo apt install gcc-8-plugin-dev` (replace 9 with whatever version of gcc you're using).  If you don't, building the plugin will result in this error ( FileNotFoundError: [Errno 2] No such file or directory: '/usr/lib/gcc/x86_64-linux-gnu/7/plugin/include/auto-host.h'
)
do sudo apt-get install python3.5
`make PYTHON=python3.5 PYTHON_CONFIG=python3.5-config` in the gcc-python-plugin
**Running**
For executing the code, you have to setup the environment first.  Add the following to your shell .*rc file:

```
export LD_LIBRARY_PATH=../gcc-python-plugin/gcc-c-api:../gcc-python-plugin
export GCC_PLUGIN_PATH=../gcc-python-plugin
./gcc-with-python.sh hls.py <file.c>
```
If you get an error like "./gcc-with-python.sh:6: command not found: gcc-7", feel free
to change the gcc version or install a different version with e.g.`sudo apt -y install gcc-7 g++-7` `sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-7 7`.  These won't change your default gcc version ( you can do that with `sudo update-alternatives --config gcc`
)
Each C file is currently taken from the `bitgpu/bench` repository as it is nicely packaged up into simple dataflow functions.


# Workflow
If you can run this next line without hitting an error, congratulations!  Your're all set up.
```
python3 mocarabe.py -dfg hgr/int_poly3 -iod 1 -ard 1 -II 1 -C 2 --place_time 0.1 --sched_method ILP
```
## Compiling Benchmarks
Our precompiled benchmarks are located in in `hgr/`. Do the following if you wish to compile your own:

1. `git checkout cgra-ilp` in the watcag/gcc-python-plugin repository.
2. Env vars for the gcc python plugin: `export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:<path/to/..>/gcc-python-plugin/gcc-c-api/:<path/to/..>/gcc-python-plugin/`
3. From this repository, to create the DFG using gcc (example: int_gaussian.graph): `./gcc-with-python.sh hls.py "bench/bitgpu/int_gaussian.c"`

For the `int_gaussian` benchmark, ouput would be in `hgr/int_gaussian/int_gaussian.hgr`.  Details on this format can be found in src/SRC_README.md under the dataflow_hypergraph heading.