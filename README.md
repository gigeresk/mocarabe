# Mocarabe

[![CI](https://github.com/gigeresk/mocarabe/actions/workflows/ci.yml/badge.svg)](https://github.com/gigeresk/mocarabe/actions/workflows/ci.yml)  

Mocarabe is a CGRA (Coarse-Grained Reconfigurable Array) architecture generator and a fully-custom toolchain. The implementation and results are discussed in [Mocarabe: High-Performance Time-Multiplexed Overlays for FPGAs](https://ieeexplore.ieee.org/document/9444076), published at FCCM 2021. This work was done by Frederick Tombs, Alireza Mellat, and Prof. Nachiket Kapre.

To get started, jump to [Toolchain setup](#toolchain-setup).

## Architecture 
The architecture consists of a grid of building blocks connected by a unidirectional torus network, as shown in the figure below. Each block contains a processing element (PE) to execute operations on incoming data and a set of NoC routers to control data movement.  

![](paper/pics/NoCdiagram.png)  

PEs store incoming operands in shift registers and select the relevant stored operands as inputs to their ALU at each cycle, as seen below.

![](paper/pics/PE.png)

The architecture is designed for statically-scheduled, time-multiplexed sharing of both routing and compute resources, with a repeating context window of length *II* (for *initiation interval*). *II* is the number of cycles in the modulo schedule found by the compiler. This makes the architecture periodic in both space (toroidal topology) and time (modulo schedule).

## Toolchain
The toolchain:
- Compiles a C kernel into a DFG
- Generates a right-sized architecture by allocating PEs
- Partitions nodes into processing elements
- Places these PEs in the grid to minimize communication cost (wirelength)
- Schedules routing and computation
- Generates both synthesizable RTL and simulation artifacts.  

Placement is done with simulated annealing and scheduling has dual strategies: an integer linear programming formulation (default) and a temporal-spatial PathFinder implementation.

<img src="paper/pics/flow.png" width="500" alt="Mocarabe architecture and EDA toolchain flow">

### Toolchain setup
```
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]

# install icarus verilog. e.g. on Ubuntu:
sudo apt install iverilog

make -C llvm_pass  # build the LLVM plugin
```
### Quick example
Here is a C kernel we can map:
```c
// int_adder_chain.c

int int_adder_chain(int x, int y, int z, int a, int* ret) {
	*ret = x+y+z+a;
}
```
Compile to a DFG, then map and simulate:
```bash
# Compile C kernel to hypergraph DFG
./llvm-with-clang.sh int_adder_chain.c hgr/

# Map to a Mocarabe architecture
  #   -II 1   : initiation interval (schedule length in cycles)
  #   -C 20   : physical channels per NoC link
  #   -iod 1  : IO-node packing density (1 IO node per PE)
  #   -ard 1  : arithmetic-node packing density (1 op per PE)
mocarabe -dfg hgr/int_adder_chain -II 1 -C 20 -iod 1 -ard 1

# Visualize the placed-and-routed design
mocarabe-viz --proj proj/int_adder_chain_*/

# Simulate the generated RTL (path printed by the command above)
cd proj/int_adder_chain_*/rtl/
iverilog -g2012 -o sim.vvp mocarabe.sv pe_2_input.sv torus_switch.sv \
          pe_srl.v pe_mux_2_input.sv pe_mux_3_input.sv SRL16E.v SRLC32E.v SRL64.v mocarabe_tb.sv
vvp sim.vvp
```


## How to Cite

If you use any part of the code or data from this repository for academic work, please cite the associated paper as follows:

```bibtex
@INPROCEEDINGS{9444076,
  author={Tombs, Frederick and Mellat, Alireza and Kapre, Nachiket},
  booktitle={2021 IEEE 29th Annual International Symposium on Field-Programmable Custom Computing Machines (FCCM)},
  title={Mocarabe: High-Performance Time-Multiplexed Overlays for FPGAs},
  year={2021},
  doi={10.1109/FCCM51124.2021.00021}
}
```
