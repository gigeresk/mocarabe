import sys
import shutil
import json
from dataflow_hypergraph import DataflowHypergraph
from gccutils import get_src_for_loc, cfg_to_idfg, invoke_dot
import gcc


def mkdir_if_needed(dir):
    if not os.path.exists(dir):
        sys.stdout.write(f"Creating {dir} directory\n")
        os.makedirs(dir)


'''
make sure to...
make PYTHON=python3 PYTHON_CONFIG=python3-config
LD_LIBRARY_PATH=:/opt/gurobi811/linux64/lib::/home/fgjtombs/code/gcc-python-plugin/gcc-c-api/:/home/fgjtombs/code/gcc-python-plugin
and
$export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/fgjtombs/code/gcc-python-plugin/gcc-c-api/:/home/fgjtombs/code/gcc-python-plugin
in gcc-with-python or equivalent, fplugin is pointed to /home/fgjtombs/code/gcc-python-plugin/python.so
'''

sys.path.append("mocarabe")
# Output the inverted DFG of a program


class OutputDFG(gcc.GimplePass):
    def execute(self, func):
        if func and func.cfg:
            H = cfg_to_idfg(func.cfg, func.decl.name)
            dataflow_hypergraph = DataflowHypergraph()
            dataflow_hypergraph = dataflow_hypergraph.unroll_dfg(H, 1)
            mkdir_if_needed('dot')
            dataflow_hgraph = DataflowHypergraph()
            G = dataflow_hgraph.to_graph()

            dot = dataflow_hgraph.to_dot(G)
            dot_file_path = 'dot/' + benchmark_name + '.dot'
            dot_file = open(dot_file_path, "w+")
            dot_file.write(dot)
            dot_file.close()
            print(f'printed to {dot_file} ')


ps = OutputDFG(name='show-gimple')
ps.register_after('cfg')
