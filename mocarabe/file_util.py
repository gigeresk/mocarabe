import os
import json


class FilePathsHelper:
    def __init__(self, root_dir_for_all_proj, benchmark_name, dir_suffix):
        self.root_dir_for_all_proj = root_dir_for_all_proj
        self.proj_dir = root_dir_for_all_proj + benchmark_name + "_" + dir_suffix + '/'

        self.partition_dir = self.proj_dir + 'partition/'
        self.netlist_dir = self.proj_dir + 'netlist/'
        self.schedule_dir = self.proj_dir + 'schedule/'
        self.log_dir = self.proj_dir + 'log/'
        self.dot_dir = self.proj_dir + 'dot/'
        self.rtl_dir = self.proj_dir + 'rtl/'
        self.hgr_dir = self.proj_dir + 'hgr/'
        self.placement_dir = self.proj_dir + 'placement/'
        self.svg_dir = self.proj_dir + 'svg/'

        self.netlist_filepath = self.proj_dir + \
            f"netlist/{benchmark_name}" + '.net'
        self.benchmark_name = benchmark_name

    def mk_proj_subdirectories(self):
        mkdir_if_needed(self.root_dir_for_all_proj)
        mkdir_if_needed(self.proj_dir)

        mkdir_if_needed(self.partition_dir)
        mkdir_if_needed(self.netlist_dir)
        mkdir_if_needed(self.schedule_dir)
        mkdir_if_needed(self.log_dir)
        mkdir_if_needed(self.dot_dir)
        mkdir_if_needed(self.rtl_dir)
        mkdir_if_needed(self.hgr_dir)
        mkdir_if_needed(self.placement_dir)
        mkdir_if_needed(self.svg_dir)

    @staticmethod
    def write_string_to_file(filename, content):
        file = open(filename, "w+")
        file.write(content)
        file.close()

    @staticmethod
    def write_list_to_file(filename, list_to_serialize):
        serialized_list = json.dumps(list_to_serialize)
        file = open(filename, "w+")
        file.write(serialized_list)
        file.close()


def mkdir_if_needed(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


def serialize_list_to_file(list_to_serialize, filename):
    serialized_list = json.dumps(list_to_serialize)

    serialization_file = open(filename, "w+")
    serialization_file.write(serialized_list + "\n")
    serialization_file.close()
