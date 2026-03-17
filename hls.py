import shutil
import json
from dataflow_hypergraph import DataflowHypergraph
from gccutils import get_mocarabe_for_loc, cfg_to_idfg, invoke_dot
import gcc
import sys

sys.path.append("mocarabe")
sys.path.append("../cgra-ilp/mocarabe")
# Output the inverted DFG of a program


class OutputDFG(gcc.GimplePass):
    def execute(self, func):
        if func and func.cfg:
            name = func.decl.name
            H = cfg_to_idfg(func.cfg, func.decl.name)

            dataflow_hypergraph = DataflowHypergraph()

            hls_dir = "hls/"
            if not os.path.exists(hls_dir):
                print("Creating 'hgr' directory")
                os.makedirs(hls_dir)
            func_dir = hls_dir + name + "/"
            if (
                os.path.exists(hls_dir + name) and len(hls_dir + name) > 2
            ):  # trying to be safe
                print("Deleting existing {} directory".format(func_dir))
                shutil.rmtree(func_dir)

            print("Creating {} directory".format(func_dir))
            os.makedirs(func_dir)

            df_hypergraph_path = func_dir + name + ".hgr"
            dataflow_hypergraph.serialize_df_hypergraph(H, df_hypergraph_path)
            print(f"Serializing dataflow hypergraph to {df_hypergraph_path}")


ps = OutputDFG(name="show-gimple")
ps.register_after("cfg")
