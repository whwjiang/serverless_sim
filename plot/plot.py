#!/usr/bin/env python

import matplotlib
matplotlib.use('Agg')

import json
import matplotlib.pyplot as plt
from operator import itemgetter


def get_slowdown(filename):
    with open(filename, 'r') as f:
        data = json.loads(f.read())
    data_sorted = sorted(data, key=itemgetter('load'))
    data_load = [entry['load'] for entry in data_sorted]
    data_slowdown99 = [entry['slowdown99'] for entry in data_sorted]
    return (data_load, data_slowdown99)


def get_latency99(filename):
    with open(filename, 'r') as f:
        data = json.loads(f.read())
    data_sorted = sorted(data, key=itemgetter('load'))
    data_load = [entry['load'] for entry in data_sorted]
    data_latency99 = [entry['latency99'] for entry in data_sorted]
    return (data_load, data_latency99)


def get_slowdown50(filename):
    with open(filename, 'r') as f:
        data = json.loads(f.read())
    data_sorted = sorted(data, key=itemgetter('load'))
    data_load = [entry['load'] for entry in data_sorted]
    data_slowdown50 = [entry['slowdown50'] for entry in data_sorted]
    return (data_load, data_slowdown50)


# Plot Lognormal Slowdown p99 -- 1 worker -- 4 cores
plt.figure()

fcfs_load, fcfs_slowdown99 = get_slowdown('../out/osdi2020/'
                                          'fcfs_log_1worker_4cores')
ps_load, ps_slowdown99 = get_slowdown('../out/osdi2020/ps_log_1worker_4cores')
ps_slowdown99.append(1000)
pc_ps_load, pc_ps_slowdown99 = get_slowdown('../out/osdi2020/'
                                            'ps_log_4workers_1core')
pc_ps_slowdown99.append(1000)
pc_load, pc_slowdown99 = get_slowdown('../out/osdi2020/'
                                      'fcfs-eb_log_4workers_1core')

plt.plot(fcfs_load, fcfs_slowdown99, marker='o', label='Late Binding')
plt.plot(fcfs_load, pc_slowdown99, marker='^',
         label='Per-Core Early Binding')
plt.plot(fcfs_load, pc_ps_slowdown99, marker='v',
         label='Per-Core Early Binding + PS')
plt.plot(fcfs_load, ps_slowdown99, marker='x',
         label='Server-Wide Early Binding + PS')

plt.xlabel('Load')
plt.ylabel('p99 Slowdown')
plt.legend()
plt.ylim(0, 10)
plt.savefig('./images/p99_log_1worker_4cores.png')


# Plot Lognormal Slowdown p50 -- 1 worker -- 4 cores
plt.figure()

fcfs_load, fcfs_slowdown50 = get_slowdown50('../out/osdi2020/'
                                            'fcfs_log_1worker_4cores')
ps_load, ps_slowdown50 = get_slowdown50('../out/osdi2020/'
                                        'ps_log_1worker_4cores')
ps_slowdown50.append(1000)
pc_ps_load, pc_ps_slowdown50 = get_slowdown50('../out/osdi2020/'
                                              'ps_log_4workers_1core')
pc_ps_slowdown50.append(1000)
pc_load, pc_slowdown50 = get_slowdown50('../out/osdi2020/'
                                        'fcfs-eb_log_4workers_1core')

plt.plot(fcfs_load, fcfs_slowdown50, marker='o', label='Late Binding')
plt.plot(fcfs_load, pc_slowdown50, marker='^',
         label='Per-Core Early Binding')
plt.plot(fcfs_load, pc_ps_slowdown50, marker='v',
         label='Per-Core Early Binding + PS')
plt.plot(fcfs_load, ps_slowdown50, marker='x',
         label='Server-Wide Early Binding + PS')

plt.xlabel('Load')
plt.ylabel('p50 Slowdown')
plt.legend()
plt.ylim(0, 10)
plt.savefig('./images/p50_log_1worker_4cores.png')


# Plot Lognormal Slowdown p99 -- 1 worker -- 12 cores
plt.figure()

fcfs_load, fcfs_slowdown99 = get_slowdown('../out/osdi2020/'
                                          'fcfs_log_1worker_12cores')
ps_load, ps_slowdown99 = get_slowdown('../out/osdi2020/ps_log_1worker_12cores')
ps_slowdown99.append(1000)
pc_ps_load, pc_ps_slowdown99 = get_slowdown('../out/osdi2020/'
                                            'ps_log_12workers_1core')
pc_ps_slowdown99.append(1000)
pc_load, pc_slowdown99 = get_slowdown('../out/osdi2020/'
                                      'fcfs-eb_log_12workers_1core')

plt.plot(fcfs_load, fcfs_slowdown99, marker='o', label='Late Binding')
plt.plot(fcfs_load, pc_slowdown99, marker='^',
         label='Per-Core Early Binding')
plt.plot(fcfs_load, pc_ps_slowdown99, marker='v',
         label='Per-Core Early Binding + PS')
plt.plot(fcfs_load, ps_slowdown99, marker='x',
         label='Server-Wide Early Binding + PS')

plt.xlabel('Load')
plt.ylabel('p99 Slowdown')
plt.legend()
plt.ylim(0, 10)
plt.savefig('./images/p99_log_1worker_12cores.png')


# Plot Lognormal Latency p99 -- 1 worker -- 12 cores
plt.figure()

fcfs_load, fcfs_latency99 = get_latency99('../out/osdi2020/'
                                          'fcfs_log_1worker_12cores')
ps_load, ps_latency99 = get_latency99('../out/osdi2020/ps_log_1worker_12cores')
ps_latency99.append(1000)
pc_ps_load, pc_ps_latency99 = get_latency99('../out/osdi2020/'
                                            'ps_log_12workers_1core')
pc_ps_latency99.append(1000)
pc_load, pc_latency99 = get_latency99('../out/osdi2020/'
                                      'fcfs-eb_log_12workers_1core')

plt.plot(fcfs_load, fcfs_latency99, marker='o', label='Late Binding')
plt.plot(fcfs_load, pc_latency99, marker='^',
         label='Per-Core Early Binding')
plt.plot(fcfs_load, pc_ps_latency99, marker='v',
         label='Per-Core Early Binding + PS')
plt.plot(fcfs_load, ps_latency99, marker='x',
         label='Server-Wide Early Binding + PS')

plt.xlabel('Load')
plt.ylabel('p99 Latency')
plt.legend()
plt.ylim(0, 1000)
plt.savefig('./images/p99_latency_log_1worker_12cores.png')


# Plot Lognormal Slowdown p50 -- 1 worker -- 12 cores
plt.figure()

fcfs_load, fcfs_slowdown50 = get_slowdown50('../out/osdi2020/'
                                            'fcfs_log_1worker_12cores')
ps_load, ps_slowdown50 = get_slowdown50('../out/osdi2020/'
                                        'ps_log_1worker_12cores')
ps_slowdown50.append(1000)
pc_ps_load, pc_ps_slowdown50 = get_slowdown50('../out/osdi2020/'
                                              'ps_log_12workers_1core')
pc_ps_slowdown50.append(1000)
pc_load, pc_slowdown50 = get_slowdown50('../out/osdi2020/'
                                        'fcfs-eb_log_12workers_1core')

plt.plot(fcfs_load, fcfs_slowdown50, marker='o', label='Late Binding')
plt.plot(fcfs_load, pc_slowdown50, marker='^',
         label='Per-Core Early Binding')
plt.plot(fcfs_load, pc_ps_slowdown50, marker='v',
         label='Per-Core Early Binding + PS')
plt.plot(fcfs_load, ps_slowdown50, marker='x',
         label='Server-Wide Early Binding + PS')

plt.xlabel('Load')
plt.ylabel('p50 Slowdown')
plt.legend()
plt.ylim(0, 10)
plt.savefig('./images/p50_log_1worker_12cores.png')


# Plot Lognormal Slowdown p99 -- 4 workers -- 12 cores
plt.figure()

fcfs_load, fcfs_slowdown99 = get_slowdown('../out/osdi2020/'
                                          'fcfs_log_4workers_12cores')
ps_load, ps_slowdown99 = get_slowdown('../out/osdi2020/'
                                      'ps_log_4workers_12cores')
ps_slowdown99.append(1000)
pc_ps_load, pc_ps_slowdown99 = get_slowdown('../out/osdi2020/'
                                            'ps_log_48workers_1core')
pc_ps_slowdown99.append(1000)
pc_load, pc_slowdown99 = get_slowdown('../out/osdi2020/'
                                      'fcfs-eb_log_48workers_1core')

plt.plot(fcfs_load, fcfs_slowdown99, marker='o', label='Late Binding')
plt.plot(fcfs_load, pc_slowdown99, marker='^',
         label='Per-Core Early Binding')
plt.plot(fcfs_load, pc_ps_slowdown99, marker='v',
         label='Per-Core Early Binding + PS')
plt.plot(fcfs_load, ps_slowdown99, marker='x',
         label='Server-Wide Early Binding + PS')

plt.xlabel('Load')
plt.ylabel('p99 Slowdown')
plt.legend()
plt.ylim(0, 10)
plt.savefig('./images/p99_log_4workers_12cores.png')


# Plot Lognormal Latency p99 -- 4 workers -- 12 cores
plt.figure()

fcfs_load, fcfs_latency99 = get_latency99('../out/osdi2020/'
                                          'fcfs_log_4workers_12cores')
ps_load, ps_latency99 = get_latency99('../out/osdi2020/'
                                      'ps_log_4workers_12cores')
ps_latency99.append(1000)
pc_ps_load, pc_ps_latency99 = get_latency99('../out/osdi2020/'
                                            'ps_log_48workers_1core')
pc_ps_latency99.append(1000)
pc_load, pc_latency99 = get_latency99('../out/osdi2020/'
                                      'fcfs-eb_log_48workers_1core')

plt.plot(fcfs_load, fcfs_latency99, marker='o', label='Late Binding')
plt.plot(fcfs_load, pc_latency99, marker='^',
         label='Per-Core Early Binding')
plt.plot(fcfs_load, pc_ps_latency99, marker='v',
         label='Per-Core Early Binding + PS')
plt.plot(fcfs_load, ps_latency99, marker='x',
         label='Server-Wide Early Binding + PS')

plt.xlabel('Load')
plt.ylabel('p99 Latency')
plt.legend()
plt.ylim(0, 1000)
plt.savefig('./images/p99_latency_log_4workers_12cores.png')


# Plot Lognormal Slowdown p50 -- 4 workers -- 12 cores
plt.figure()

fcfs_load, fcfs_slowdown50 = get_slowdown50('../out/osdi2020/'
                                            'fcfs_log_4workers_12cores')
ps_load, ps_slowdown50 = get_slowdown50('../out/osdi2020/'
                                        'ps_log_4workers_12cores')
ps_slowdown50.append(1000)
pc_ps_load, pc_ps_slowdown50 = get_slowdown50('../out/osdi2020/'
                                              'ps_log_48workers_1core')
pc_ps_slowdown50.append(1000)
pc_load, pc_slowdown50 = get_slowdown50('../out/osdi2020/'
                                        'fcfs-eb_log_48workers_1core')

plt.plot(fcfs_load, fcfs_slowdown50, marker='o', label='Late Binding')
plt.plot(fcfs_load, pc_slowdown50, marker='^',
         label='Per-Core Early Binding')
plt.plot(fcfs_load, pc_ps_slowdown50, marker='v',
         label='Per-Core Early Binding + PS')
plt.plot(fcfs_load, ps_slowdown50, marker='x',
         label='Server-Wide Early Binding + PS')

plt.xlabel('Load')
plt.ylabel('p50 Slowdown')
plt.legend()
plt.ylim(0, 10)
plt.savefig('./images/p50_log_4workers_12cores.png')

# Plot Lognormal Slowdown p99 -- 4 workers -- unbalanced
plt.figure()

fcfs_load, fcfs_slowdown99 = get_slowdown('../out/osdi2020/'
                                          'fcfs_log_4workers_12cores')
ps_load, ps_slowdown99 = get_slowdown('../out/osdi2020/'
                                      'ps_log_4workers_unbalanced')
ps_slowdown99.append(1000)
ps_prop_load, ps_prop_slowdown99 = get_slowdown('../out/osdi2020/ps_log_'
                                                '4workers_proportional')
ps_prop_slowdown99.append(1000)
pc_ps_load, pc_ps_slowdown99 = get_slowdown('../out/osdi2020/'
                                            'ps_log_48workers_1core')
pc_ps_slowdown99.append(1000)
pc_load, pc_slowdown99 = get_slowdown('../out/osdi2020/'
                                      'fcfs-eb_log_48workers_1core')

plt.plot(fcfs_load, fcfs_slowdown99, marker='o', label='Late Binding')
plt.plot(fcfs_load, pc_slowdown99, marker='^',
         label='Per-Core Early Binding')
plt.plot(fcfs_load, pc_ps_slowdown99, marker='v',
         label='Per-Core Early Binding + PS')
plt.plot(fcfs_load, ps_slowdown99, marker='x',
         label='Server-Wide Early Binding + PS')
plt.plot(fcfs_load, ps_prop_slowdown99, marker='x',
         label='Server-Wide Early Binding + Proportional PS')

plt.xlabel('Load')
plt.ylabel('p99 Slowdown')
plt.legend()
plt.ylim(0, 10)
plt.savefig('./images/p99_log_4workers_unbalanced.png')


# Plot Lognormal Latency p99 -- 4 workers -- unbalanced
plt.figure()

fcfs_load, fcfs_latency99 = get_latency99('../out/osdi2020/'
                                          'fcfs_log_4workers_12cores')
ps_load, ps_latency99 = get_latency99('../out/osdi2020/'
                                      'ps_log_4workers_unbalanced')
ps_latency99.append(1000)
ps_prop_load, ps_prop_latency99 = get_latency99('../out/osdi2020/ps_log_'
                                                '4workers_proportional')
ps_prop_latency99.append(1000)
pc_ps_load, pc_ps_latency99 = get_latency99('../out/osdi2020/'
                                            'ps_log_48workers_1core')
pc_ps_latency99.append(1000)
pc_load, pc_latency99 = get_latency99('../out/osdi2020/'
                                      'fcfs-eb_log_48workers_1core')

plt.plot(fcfs_load, fcfs_latency99, marker='o', label='Late Binding')
plt.plot(fcfs_load, pc_latency99, marker='^',
         label='Per-Core Early Binding')
plt.plot(fcfs_load, pc_ps_latency99, marker='v',
         label='Per-Core Early Binding + PS')
plt.plot(fcfs_load, ps_latency99, marker='x',
         label='Server-Wide Early Binding + PS')
plt.plot(fcfs_load, ps_prop_latency99, marker='x',
         label='Server-Wide Early Binding + Proportional PS')

plt.xlabel('Load')
plt.ylabel('p99 Latency')
plt.legend()
plt.ylim(0, 1000)
plt.savefig('./images/p99_latency_log_4workers_unbalanced.png')


# Plot Lognormal Slowdown p50 -- 4 workers -- unbalanced
plt.figure()

fcfs_load, fcfs_slowdown50 = get_slowdown50('../out/osdi2020/'
                                            'fcfs_log_4workers_12cores')
ps_load, ps_slowdown50 = get_slowdown50('../out/osdi2020/'
                                      'ps_log_4workers_unbalanced')
ps_slowdown50.append(1000)
ps_prop_load, ps_prop_slowdown50 = get_slowdown50('../out/osdi2020/ps_log_'
                                                  '4workers_proportional')
ps_prop_slowdown50.append(1000)
pc_ps_load, pc_ps_slowdown50 = get_slowdown50('../out/osdi2020/'
                                              'ps_log_48workers_1core')
pc_ps_slowdown50.append(1000)
pc_load, pc_slowdown50 = get_slowdown50('../out/osdi2020/'
                                        'fcfs-eb_log_48workers_1core')

plt.plot(fcfs_load, fcfs_slowdown50, marker='o', label='Late Binding')
plt.plot(fcfs_load, pc_slowdown50, marker='^',
         label='Per-Core Early Binding')
plt.plot(fcfs_load, pc_ps_slowdown50, marker='v',
         label='Per-Core Early Binding + PS')
plt.plot(fcfs_load, ps_slowdown50, marker='x',
         label='Server-Wide Early Binding + PS')
plt.plot(fcfs_load, ps_prop_slowdown50, marker='x',
         label='Server-Wide Early Binding + Proportional PS')

plt.xlabel('Load')
plt.ylabel('p50 Slowdown')
plt.legend()
plt.ylim(0, 10)
plt.savefig('./images/p50_log_4workers_unbalanced.png')
