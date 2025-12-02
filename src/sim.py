#!/usr/bin/env python3

import numpy as np
import sys
import json
import simpy
import logging
import argparse

# import matplotlib.pyplot as plt
from util.histogram import *

from host.host import *
from controller.controller import *
from request.request_generator import *
from request.interarrival_generator import *


gen_dict = {
    'heavy_tail': 'HeavyTailRequestGenerator',
    'poisson_arrival': 'PoissonArrivalGenerator',
    'lognormal_arrival': 'LogNormalArrivalGenerator',
    'base_arrival': 'InterArrivalGenerator',
    'exponential_request': 'ExponentialRequestGenerator',
    'lognormal_request': 'LogNormalRequestGenerator',
    'normal_request': 'NormalRequestGenerator',
    'pareto_request': 'ParetoRequestGenerator',
    'global': 'GlobalQueueHost',
    'local': 'MultiQueueHost',
    'shinjuku':  'ShinjukuHost',
    'perflow': 'PerFlowQueueHost',
    'staticcore': 'StaticCoreAllocationHost',
    'latebinding': 'LateBindingController',
    'leastloaded': 'LeastLoadedController',
    'locality': 'LocalityController',
    'leastloadedsrpt': 'LeastLoadedSRPTController',
    'lps': 'LPSController',
    'heterogeneousll': 'HeterogeneousLeastLoadedController',
    'proportionalll': 'ProportionalLeastLoadedController',
    'random': 'RandomController'
}


def main():
    # parser = optparse.OptionParser()
    parser = argparse.ArgumentParser(description='')

    parser.add_argument('-v', '--verbose', dest='verbose',
                        action='count', help='Increase verbosity (specify'
                        ' multiple times for more)', default=0)
    parser.add_argument('-g', '--print-hist', action='store_true', dest='hist',
                        help='Print request latency histogram', default=False)
    parser.add_argument('-s', '--seed', dest='seed', action='store',
                        help='Set the seed for request generator', default=100, type=int)
    parser.add_argument('-t', '--sim_time', dest='sim_time', action='store',
                        help='Set the simulation time', default=3600, type=int)
    parser.add_argument('--workload-conf', dest='work_conf', action='store',
                        help='Configuration file for the load generation'
                        ' functions', default="../config/work.json", type=str)

    group = parser.add_argument_group('Controller and Host Options')
    group.add_argument('--controller-type', dest='controller_type',
                       action='store', help=('Set the controller configuration'
                                             ' (late binding, least loaded,'
                                             ' lps)'),
                       default='latebinding')
    group.add_argument('--host-type', dest='host_type', action='store',
                       help=('Set the host configuration (global queue,'
                             ' local queue, shinjuku, per flow queues,'
                             ' static core allocation)'), default='global', type=str)
    group.add_argument('--deq-cost', dest='deq_cost', action='store',
                       help='Set the dequeuing cost', default=0.0, type=float)
    parser.add_argument('-c', '--cores', dest='cores', action='store',
                        help='Set the number of cores of the system',
                        default=8, type=int)
    parser.add_argument('-w', '--workers', dest='workers', action='store',
                        help='Set the number of worker hosts of the system',
                        default=1, type=int)
    parser.add_argument('-d', '--window', dest='window', action='store',
                        help='Set time for simulation time start',
                        default=0.0, type=float)
    parser.add_argument('--capacity', dest='capacity', action='store',
                        help=('Set the number of concurrent requests that can'
                              ' be executing on each worker host'),
                        default=12, type=int)
    parser.add_argument('--latency', dest='latency', action='store',
                        help='Set the controller-worker communication latency',
                        default=0.0, type=float)


    parser.add_argument("--steal-work", dest="steal_work", action="store_true",
                        help="Enable host work stealing", default=False)
    parser.add_argument("--hot", dest="steal_hot", action="store_true",
                        help="Only steal hot work from hosts", default=False)
    parser.add_argument("--steal-max", dest="steal_maximum", action="store",
                        help="Maximum request a host can steal at a time", default=20, type=int)
    parser.add_argument("--steal-timer", dest="steal_timer", action="store",
                        help="Time interval for host work stealing", default=60, type=float)

    # TODO: (More general) Make more request generators??
    # TODO: Set default costs more accurate to read papers
    parser.add_argument("--cost-cold", dest="cost_cold", action="store",
                        help="Cold startup time cost (milliseconds)", default=500, type=int)
    parser.add_argument("--cost-hot", dest="cost_hot", action="store",
                        help="Hot startup time cost (milliseconds)", default=150, type=int)


    group.add_argument('--queue-policy', dest='queue_policy', action='store',
                       help=('Set the queue policy to be followed by the per'
                             ' flow queue, ignored in any other queue'
                             ' configuration'), default='FlowQueues', type=str)
    parser.add_argument_group(group)

    group = parser.add_argument_group('Print Options')
    group.add_argument('--print-values', dest='print_values',
                       action='store_true', help='Print all the latencies for'
                       ' each flow', default=False)
    group.add_argument('--output-file', dest='output_file', action='store',
                       help='File to print all latencies', default=None)

    opts = parser.parse_args()

    # Seeding
    if opts.seed:
        random.seed(int(opts.seed))
        np.random.seed(int(opts.seed))

    # Setup logging
    log_level = logging.WARNING
    if opts.verbose == 1:
        log_level = logging.INFO
    elif opts.verbose >= 2:
        log_level = logging.DEBUG
    logging.basicConfig(level=log_level)

    # Initialize the different components of the system
    env = simpy.Environment()

    # Parse the configuration file
    with open(opts.work_conf, 'r') as f:
        flow_config = json.loads(f.read())

    # Create a histogram per flow and a global histogram
    histograms = Histogram(env, int(opts.sim_time), len(flow_config),
                           float(opts.cores), flow_config, opts)

    # Get the queue configuration
    ctrl_conf = getattr(sys.modules[__name__], gen_dict[opts.controller_type])
    sim_ctrl = ctrl_conf(env, int(opts.workers), int(opts.cores),
                         int(opts.capacity), float(opts.latency), flow_config,
                         histograms, opts)

    # TODO:Update so that it's parametrizable
    # print "Warning: Need to update sim.py for parameterization and Testing"
    # First list is time slice, second list is load
    # sim_host = StaticCoreAllocationHost(env, int(opts.cores),
    #                                     float(opts.deq_cost), [0.0, 0.0],
    #                                     histograms, len(flow_config),
    #                                     [0.4, 0.4])

    multigenerator = MultipleRequestGenerator(env, sim_ctrl)

    # Create one object per flow
    for flow in flow_config:
        params = flow
        inter_gen = getattr(sys.modules[__name__],
                            gen_dict[params["inter_gen"]])
        work_gen = getattr(sys.modules[__name__],
                           gen_dict[params["work_gen"]])

        # Need to generate less load when we have shinjuku because one
        # of the cores is just the dispatcher
        if (opts.host_type == "shinjuku"):
            opts.cores = int(opts.cores) - 1

        multigenerator.add_generator(work_gen(histograms, env, sim_ctrl,
                                              inter_gen,
                                              (int(opts.workers) *
                                               int(opts.cores)),
                                              params))

    multigenerator.begin_generation()

    # Run the simulation
    try:
        env.run(until=1000 * opts.sim_time * 2)
    except EndException:
        # Print results in json format
        histograms.print_info()


if __name__ == "__main__":
    main()
