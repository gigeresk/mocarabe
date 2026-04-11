import abc
import itertools
import os
from datetime import datetime


import func_timeout as timeout

import timeit

from .pathfinder_scheduler import UnroutableError


class SchedulerStrategy(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def schedule(self):
        pass

    def run_scheduling_with_timeout(
        self,
        device,
        netlist,
        place_time,
        file_helper,
        num_partitions_given_to_operator,
        tag,
        sched_time=30,
        seed=0,
    ):
        if not os.path.exists("log"):
            print("Creating 'log' directory")
            os.makedirs("log")
        if not os.path.exists("results"):
            print("Creating 'results' directory")
            os.makedirs("results")

        rerun = True
        MAX_RUN_COUNT = 10
        TIMEOUT_IN_SECONDS = sched_time
        dataflow_mode = False
        io_pes = []
        boundingBoxEnabled = False

        assert device.Nx > 0, "Nx must be defined and > 0"
        assert device.Ny > 0, "Ny must be defined and > 0"
        assert device.P > 0, "P must be defined and > 0"
        assert device.physical_channels > 0, "C must be defined and > 0"
        assert device.T > 0, "T must be defined and >= 0"
        assert device.IO_O > 0, "IO_I must be defined and > 0"
        schedule_start = datetime.now()
        if "*" not in num_partitions_given_to_operator:
            num_partitions_given_to_operator["*"] = 0
        if "+" not in num_partitions_given_to_operator:
            num_partitions_given_to_operator["+"] = 0
        if "IN" not in num_partitions_given_to_operator:
            num_partitions_given_to_operator["IN"] = 0
        if "OUT" not in num_partitions_given_to_operator:
            num_partitions_given_to_operator["OUT"] = 0

        def run_count(c=itertools.count(1)):
            return next(c)

        current_run_count = run_count()

        if not os.path.exists(file_helper.log_file):
            # header: always keep up to date
            log_file = open(file_helper.log_file, "a+")
            header_string = (
                "%s, " % file_helper.benchmark_name
                + "Nx, "
                + "Ny, "
                + "unroll_factor, "
                + "P, "
                + "C, "
                + "IO_O, "
                + "T, "
                + "II, "
                + "place_time, "
                + "schedule_time, "
                + "run_count, "
                + "tag (special), "
                + "*, "
                + "+, "
                + "IN, "
                + "OUT, "
                + "NumVars, "
                + "NumConstrs, "
                + ", success\n"
            )
            log_file.write(header_string)
            log_file.close()

        while current_run_count < MAX_RUN_COUNT:
            try:
                log_string = (
                    "#starting: %s, " % file_helper.benchmark_name
                    + "%d, " % device.Nx
                    + "%d, " % device.Ny
                    + "%d, " % device.P
                    + "%d, " % device.physical_channels
                    + "%d, " % device.T
                    + "%d, " % device.II
                    + "%s, " % tag
                )
                dateTimeObj = datetime.now()
                log_string = log_string + " at {0}\n".format(
                    dateTimeObj.strftime("%d-%m-%y_%H:%M:%S")
                )

                print(log_string)

                log_file = open(file_helper.log_file, "a+")
                log_file.write(log_string)
                log_file.close()

                scheduled_netlist, num_vars, num_constrs = timeout.func_timeout(
                    TIMEOUT_IN_SECONDS,
                    self.schedule,
                    args=(
                        [
                            device,
                            dataflow_mode,
                            netlist,
                            io_pes,
                            boundingBoxEnabled,
                            file_helper.netlist_filepath,
                            file_helper.benchmark_name,
                            file_helper.schedule_filepath,
                            file_helper,
                            sched_time,
                            seed,
                        ]
                    ),
                )

                schedule_time = datetime.now() - schedule_start
                log_string = (
                    "%s, " % file_helper.benchmark_name
                    + "%d, " % device.Nx
                    + "%d, " % device.Ny
                    + "%d, " % device.unroll_factor
                    + "%d, " % device.P
                    + "%d, " % device.physical_channels
                    + "%d, " % device.IO_O
                    + "%d, " % device.T
                    + "%d, " % device.II
                    + "%f, " % place_time.seconds
                    + "%f, " % schedule_time.seconds
                    + "%d, " % current_run_count
                    + "%s, " % tag
                    + "%d, " % num_partitions_given_to_operator["*"]
                    + "%d, " % num_partitions_given_to_operator["+"]
                    + "%d, " % num_partitions_given_to_operator["IN"]
                    + "%d, " % num_partitions_given_to_operator["OUT"]
                    + "%d, " % num_partitions_given_to_operator["OUT"]
                    + "%d, " % num_partitions_given_to_operator["OUT"]
                    + "%d, " % num_vars
                    + "%d, " % num_constrs
                    + ", success "
                )

                """ write to file"""
                # file_helper.schedule_filepath = file_helper.schedule_filepath = file_helper.schedule_dir  +'-ggNx%d-Ny%d-C%d-P%d-T%d.sol' % ( device.Nx, device.Ny, device.physical_channels, device.P, device.T)
                # solFile = open(file_helper.schedule_filepath, "w+")
                # solFile.write( scheduled_netlist.__str__() )
                # solFile.close()

                dateTimeObj = datetime.now()
                log_string = log_string + "#done at {0}\n".format(
                    dateTimeObj.strftime("%d-%m-%y_%H:%M:%S")
                )
                print(log_string)

                log_file = open(file_helper.log_file, "a+")

                log_file.write(log_string)
                log_file.close()

                return scheduled_netlist

            # except GurobiError as e:
            #     print('Error code ' + str(e.errno) + ": " + str(e))
            #     t1 = timeit.default_timer()
            #     log_string = "Gurobi ERROR -" + log_string
            #     log_string = '%s, ' % file_helper.benchmark_name +\
            #             '%d, ' % device.Nx +\
            #             '%d, ' % device.Ny+\
            #             '%d, ' % device.unroll_factor +\
            #             '%d, ' % device.P +\
            #             '%d, ' % device.physical_channels +\
            #             '%d, ' % device.IO_O +\
            #             '%d, ' % device.T +\
            #             '%d, ' % device.II+\
            #             '%f, ' % place_time.seconds +\
            #             '%f, ' % '-1' +\
            #             '%d, ' % current_run_count +\
            #             '%s, ' % tag +\
            #             '%d, ' % num_partitions_given_to_operator['*'] +\
            #             '%d, ' % num_partitions_given_to_operator['+'] +\
            #             '%d, ' % num_partitions_given_to_operator['IN'] +\
            #             '%d, ' % num_partitions_given_to_operator['OUT'] +\
            #             '%d, ' % num_vars +\
            #             '%d, ' % num_constrs +\
            #             "gurobi error " + str(e.errno) + "\n"
            #     print(log_string)
            #     log_file = open(file_helper.log_file, "a+")
            #     log_file.write(log_string)
            #     log_file.close()

            #     current_run_count = run_count()
            # except AttributeError:
            #     log_string = '#%s, ' % benchmark + '%d, ' % device.Nx + '%d, ' % device.Ny+ '%d, ' % device.P + '%d, ' % device.physical_channels +'%d, ' % device.T+'%d, ' % device.II
            #     print(' Gurobi encountered an attribute error')
            #     if rerun:
            #         print('attrRe-running assuming we did not allocate enough C')
            #         print('Abort the process if this is not the case')
            #         log_string = log_string + "attrre-running assuming we did not allocate enough C\n"
            #     else:
            #         t1 = timeit.default_timer()
            #         log_string = "ATTRIBUTE ERROR -" + log_string
            #         log_string += '%s, ' % benchmark +\
            #             '%d, ' % device.Nx +\
            #             '%d, ' % device.Ny+\
            #             '%d, ' % device.unroll_factor +\
            #             '%d, ' % device.P +\
            #             '%d, ' % device.physical_channels +\
            #             '%d, ' % device.IO_O +\
            #             '%d, ' % device.T +\
            #             '%d, ' % device.II+\
            #             '-1, ' +\
            #             '-1, ' +\
            #             '-1, ' +\
            #             '-1, ' +\
            #             '%d, ' % Run.count +\
            #             '%f, ' % (t1-t0) +\
            #             '%s, ' % tag +\
            #             "attribute error \n"
            #     print(log_string)
            #     log_file = open(file_helper.log_file, "a+")
            #     log_file.write(log_string)
            #     log_file.close()

            #     if not rerun: #don't rerun if you don't wanna rerun
            #         return

            #     Run.count = Run.count + 1
            except AssertionError:
                print("Encountered an assertion error")
                log_string = (
                    "#%s, " % file_helper.benchmark_name
                    + "%d, " % device.Nx
                    + "%d, " % device.Ny
                    + "%d, " % device.P
                    + "%d, " % device.physical_channels
                    + "%d, " % device.T
                    + "%d, " % device.II
                )
                print(f"rerun: {rerun}")

                if rerun:  # TODO??
                    if device.T == 1:
                        print("Re-running assuming we did not allocate enough C")
                        log_string = (
                            log_string
                            + "re-running assuming we did not allocate enough C\n"
                            + "%d"
                        )
                    else:
                        print("Re-running assuming we did not allocate enough C")
                        print("Abort the process if this is not the case")
                        log_string = (
                            log_string
                            + "re-running assuming we did not allocate enough C\n"
                        )
                else:
                    t1 = timeit.default_timer()
                    log_string = "ASSERTION ERROR -" + log_string
                    log_string += (
                        "%s, " % file_helper.benchmark_name
                        + "%d, " % device.Nx
                        + "%d, " % device.Ny
                        + "%d, " % device.unroll_factor
                        + "%d, " % device.P
                        + "%d, " % device.physical_channels
                        + "%d, " % device.IO_O
                        + "%d, " % device.T
                        + "%d, " % device.II
                        + "%f, " % place_time.seconds
                        + "%f, " % "-1"
                        + "%d, " % current_run_count
                        + "%s, " % tag
                        + "%d, " % num_partitions_given_to_operator["*"]
                        + "%d, " % num_partitions_given_to_operator["+"]
                        + "%d, " % num_partitions_given_to_operator["IN"]
                        + "%d, " % num_partitions_given_to_operator["OUT"]
                        + "%d, " % num_vars
                        + "%d, " % num_constrs
                        + "assertion error(infeasible) \n"
                    )
                print(log_string)
                log_file = open(file_helper.log_file, "a+")
                log_file.write(log_string)
                log_file.close()

                current_run_count = run_count()
            except UnroutableError:
                print("Encountered an unroutable error")
                log_string = (
                    "#%s, " % file_helper.benchmark_name
                    + "%d, " % device.Nx
                    + "%d, " % device.Ny
                    + "%d, " % device.P
                    + "%d, " % device.physical_channels
                    + "%d, " % device.T
                    + "%d, " % device.II
                )
                print(f"rerun: {rerun}")

                if rerun:
                    if device.T == 1:
                        print("unrRe-running assuming we did not allocate enough C")
                        log_string = (
                            log_string
                            + "re-running assuming we did not allocate enough C\n"
                            + "%d"
                        )
                    else:
                        print("Re-running assuming we did not allocate enough C")
                        print("Abort the process if this is not the case")
                        log_string = (
                            log_string
                            + "unrre-running assuming we did not allocate enough C\n"
                        )
                else:
                    t1 = timeit.default_timer()
                    log_string = "UNROUTABLE ERROR -" + log_string
                    log_string += (
                        "%s, " % file_helper.benchmark_name
                        + "%d, " % device.Nx
                        + "%d, " % device.Ny
                        + "%d, " % device.unroll_factor
                        + "%d, " % device.P
                        + "%d, " % device.physical_channels
                        + "%d, " % device.IO_O
                        + "%d, " % device.T
                        + "%d, " % device.II
                        + "%f, " % place_time.seconds
                        + "%f, " % "-1"
                        + "%d, " % current_run_count
                        + "%s, " % tag
                        + "%d, " % num_partitions_given_to_operator["*"]
                        + "%d, " % num_partitions_given_to_operator["+"]
                        + "%d, " % num_partitions_given_to_operator["IN"]
                        + "%d, " % num_partitions_given_to_operator["OUT"]
                        + "%d, " % num_vars
                        + "%d, " % num_constrs
                        + "unroutable error\n"
                    )
                print(log_string)
                log_file = open(file_helper.log_file, "a+")
                log_file.write(log_string)
                log_file.close()

            except timeout.FunctionTimedOut:
                dateTimeObj = datetime.now()
                log_string = "#{0} timeout at {1}\n".format(
                    file_helper.benchmark_name,
                    dateTimeObj.strftime("%d-%m-%y_%H:%M:%S"),
                )
                t1 = timeit.default_timer()
                log_string += (
                    "%s, " % file_helper.benchmark_name
                    + "%d, " % device.Nx
                    + "%d, " % device.Ny
                    + "%d, " % device.unroll_factor
                    + "%d, " % device.P
                    + "%d, " % device.physical_channels
                    + "%d, " % device.IO_O
                    + "%d, " % device.T
                    + "%d, " % device.II
                    + "%f, " % place_time.seconds
                    + "-1, "
                    + "%d, " % current_run_count
                    + "%s, " % tag
                    + "%d, " % num_partitions_given_to_operator["*"]
                    + "%d, " % num_partitions_given_to_operator["+"]
                    + "%d, " % num_partitions_given_to_operator["IN"]
                    + "%d, " % num_partitions_given_to_operator["OUT"]
                    + "%d, " % num_vars
                    + "%d, " % num_constrs
                    + "timeout \n"
                )

                log_file = open(file_helper.log_file, "a+")
                log_file.write(log_string)
                log_file.close()
                return

            current_run_count = run_count()
            device.physical_channels = 1 + device.physical_channels
            if device.physical_channels == 3:
                device.noc_pipelining_stages += 1


class PathfinderScheduler(SchedulerStrategy):
    from .pathfinder_scheduler import schedule


class IlpScheduler(SchedulerStrategy):
    from .ilp_scheduler_scip import schedule
