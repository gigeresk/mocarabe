# src/ README

## auto.py
auto.py is the driver for tor the Mocarabe compiler.  
e.g. `python3 auto.py -dfg hls/int_poly3 -iod 1 -ard 1 -II 1 -C 2 --place_time 0.1 --sched_method ILP -T 1`

### Command line arguments

- `-dfg`: path to the dataflow graph directory
- `-II`: initiation interval
- `-T`: schedule length: this should be exactly the same as     `II`.  (T is the parameter that the ILP scheduler uses, while II is used to determine resource sharing)
- `--log`: Log output is written to this `csv` around schedule time (lines commented ('#') when scheduling starts and when C has to be incremented, but full line taken up on final success/failure).  Look at `src/scheduler/__init__.py` for details.
- `--tag`: A log feature: a column is taken up by this string. Useful in scripts when comparing two approaches (e.g. "PF" or "ILP", as those aren't logged (though maybe they should be))
- `--place_time`: Annealing placement needs a time (it's not accurate, it somehow finds an iteration count based on this number and some other factor- could change this with experimentation).  For something in the order of 4x4, 0.1-0.2 is sufficient.  For the largest benchmarks, and for experiments, 1 is my go-to.
- `--sched_method`: ILP or PF.  Default is ILP.
- `-iod`: Diffusion factor for IO PEs
- `-ard`: Diffusion factor for +/* PEs

## dataflow_hypergraph
We use the `halp` package to represent dataflow graphs (DFGs) in memory, as hypergraphs.  The dataflow_hypergraph module has many useful functions (and so does `halp` itself: check their docs [here](https://murali-group.github.io/halp/) if you need to do some tricky graph manipulation stuff).  DataflowHypergraph, the class in this module, inherits from `halp`'s DirectedHypergraph.

This code is also used to extract the DFG from the C code with gcc (not covered here).  Of note are
- unroll_dfg: dfg-level unroll will give the compiler a bigger problem to solve (as opposed to the array-level unroll where we tile the smaller array over the chip )
- functions like extract_* (e.g. extract_node_arithmetic_operators) and ordered_node_id_iterator are very useful to pull information out from the DFG.
A note on DFG serialization:
I can't recall where this format comes from (it isn't the hmetis format, it may be proprietary).  
Looking at `hls/int_poly3/int_poly3.hgr` (# indicates comments and these are not present in the real file):

```
9 10    # 9 hyperedges, 10 nodes: nodes first
7: 1    # 1, c, x, 5 are all inputs
8: *    # +, * are all operators
9: y    # y is the sole output
3: +
6: +
1: x
0: *
5: *
2: c
4: 5
--      # hyperedges now
5 6     # 5->6: this hyperedge is from 5 (*) to 6 (+)
8 9 
6 8 
0 3 
3 5 
2 0 
1 8 0 5 # this is a multi-fanout: from 1 (x) to 8 (*), 0 (*), 5 (*) 
7 6 
4 3
```
Note that DataflowHypergraph denotes nodes as str integers indexed at 0 (e.g. '0','1','2',etc.) and hyperedges start at 'e1': e.g. 'e1', 'e2', 'e3', etc. 

## device
The Device class in the device module is strictly used to encapsulate certain parameters.

# CAD Flow (after gcc)
## pe_allocator

A PE allocator takes as input a DataflowHypergraph, II, diffusion factors (for now), and optionally device constraints and returns an array of heterogeneous PEs (and the array's dimensions).  
- `ClosestFactorsAllocator` attempts to allocate just enough PEs ("system size") for every PE to be occupied every cycle.  Array dimensions Nx, Ny are the closest factors of the system size.  If a system size is prime it's incremented by 1.

- `ConstrainedClosestFactorsAllocator` should function much like its unconstrained counterpart, but should be given a pattern of what cols/rows can hold what kind of PE.  **This is a work in progress and should be tested further. **

- Ideal allocator should take maximimum array dimensions as an input (e.g. 19x69) and go for a far more square approach: no 'skinny' (e.g. 2x17) arrays.  Just increment the system size.

## placer
Placing and partitioning is in the `placer` module.  The current flow is ILP DFG Partitioning + Annealing placement of those partitions, but placement of DFG nodes directly with annealing also exists in the codebase.

The `simanneal` library is powerful and easy to use.  

## scheduler
The scheduler currently has two strategies, an ILP formulation and a pathfinder implementation.  Logging is taken care of in `/scheduler/__init__.py` (code is shared between ILP and PF).

### ILP Scheduler
Please refer to the (first?) paper for an overview of constraints/objective function.

### PF Scheduler
Refer to the reference paper for some information (A Bandwidth-Optimized Routing Algorithm for Hybrid FPGA Networks-on-Chip).  This code is optimized in terms of runtime but is more complicated to implement, and less effective, than ILP.  The ResourceGraph class in src/resource_graph.py is of note.  This code has some good debugging tools built in.

## rtl_gen
A typical rtl_gen script workflow (see hwgen_develop.py) is
```
# after scheduling, read in values from the solution file
h,v,enter,exit_, T = RTLGenerator.deserialize_schedule( sched_filename, Nx, Ny, C, P, T ) 

# E-bound/N-bound/PE-bound switch context memories are generated and written into a project-specific rtl/ directory
RTLGenerator.generate_and_write_noc_mux_memories( args.proj + f'rtl/', h, v, enter,exit_, Nx, Ny, C, P, T) 
...
#for every net, a path with resource graph nodes is compiled
net_paths = RTLGenerator.get_net_path_nodes( dataflow_hgraph, resource_graph, device, h, v, enter, exit_ )

# generate PE-internal context memories
op_addresses, op_port_select = RTLGenerator.generate_and_write_pe_memories( args.proj, resource_graph, net_paths, dataflow_hgraph,placement_result, enter, exit_, C, T, pe_pipelining_stages, Nx, Ny, NUM_OPERANDS,IO_I )

```


## Goals/TODO (for maintainers)

### pe_allocator

Support constraints fully, no skinny arrays at all

### placer

Get rid of the simanneal place_time input; find a good way to give the tool enough iterations