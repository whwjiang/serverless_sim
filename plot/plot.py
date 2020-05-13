#!/usr/bin/env python

import matplotlib
matplotlib.use('Agg')

import json
import matplotlib.pyplot as plt
from operator import itemgetter

MARKER_SIZE = 15.0
LABEL_SIZE = 40.0
LEGEND_SIZE = 36
TICK_SIZE = 36
LINE_WIDTH = 5.0

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


# Plot Lognormal Slowdown p99 -- 1 worker -- 12 cores
plt.figure(figsize=(20,15))

lb_load, lb_slowdown99 = get_slowdown('../out/osdi2020/'
                                      'fcfs_log_1worker_12cores')
ps_ps_load, ps_ps_slowdown99 = get_slowdown(
        '../out/osdi2020/ps_log_1worker_12cores')
ps_ps_slowdown99.append(1000)
pc_ps_load, pc_ps_slowdown99 = get_slowdown('../out/osdi2020/'
                                            'ps_log_12workers_1core')
pc_ps_slowdown99.append(1000)
random_pc_ps_load, random_pc_ps_slowdown99 = get_slowdown(
        '../out/osdi2020/random_ps_log_12workers_1core')
random_pc_ps_slowdown99.append(1000)
pc_fcfs_load, pc_fcfs_slowdown99 = get_slowdown('../out/osdi2020/'
                                                'fcfs-eb_log_12workers_1core')
random_pc_fcfs_load, random_pc_fcfs_slowdown99 = get_slowdown(
        '../out/osdi2020/random_fcfs-eb_log_12workers_1core')
random_pc_fcfs_load, random_pc_fcfs_slowdown99 = get_slowdown(
        '../out/osdi2020/random_fcfs-eb_log_12workers_1core')

plt.plot(lb_load, lb_slowdown99, marker='o', label='Late Binding',
         color='firebrick', linewidth=LINE_WIDTH, markersize=MARKER_SIZE)
plt.plot(lb_load, pc_fcfs_slowdown99, marker='^', color='olive',
         label='E / C / L / FCFS', linewidth=LINE_WIDTH,
         markeredgewidth=LINE_WIDTH / 2.0, markersize=MARKER_SIZE)
plt.plot(lb_load, pc_ps_slowdown99, marker='v', color='darkorchid',
         label='E / C / L / PS', linewidth=LINE_WIDTH,
         markeredgewidth=LINE_WIDTH / 2.0, markersize=MARKER_SIZE)
plt.plot(lb_load, random_pc_fcfs_slowdown99, marker='*', color='teal',
         label='E / C / R / FCFS', linewidth=LINE_WIDTH,
         markeredgewidth=LINE_WIDTH / 2.0, markersize=MARKER_SIZE)
plt.plot(lb_load, random_pc_ps_slowdown99, marker='s', color='blue',
         label='E / C / R / PS', linewidth=LINE_WIDTH,
         markeredgewidth=LINE_WIDTH / 2.0, markersize=MARKER_SIZE)
plt.plot(lb_load, ps_ps_slowdown99, marker='x', color='darkgreen',
         linewidth=LINE_WIDTH, markeredgewidth=LINE_WIDTH / 2.0,
         markersize=MARKER_SIZE, label='E / S / * / PS')

plt.xlabel('Load', fontsize=LABEL_SIZE)
plt.ylabel('99% Slowdown', fontsize=LABEL_SIZE)
plt.legend(ncol=2, fontsize=LEGEND_SIZE, loc='upper left')
plt.ylim(0, 10)
plt.xlim(0, 1)
plt.xticks(fontsize=TICK_SIZE)
plt.yticks(fontsize=TICK_SIZE)
plt.savefig('./images/p99_log_1worker_12cores.png')


# Plot Lognormal Latency p99 -- 1 worker -- 12 cores
plt.figure(figsize=(20,15))

lb_load, lb_latency99 = get_latency99('../out/osdi2020/'
                                      'fcfs_log_1worker_12cores')
ps_ps_load, ps_ps_latency99 = get_latency99(
        '../out/osdi2020/ps_log_1worker_12cores')
ps_ps_latency99.append(1000)
pc_ps_load, pc_ps_latency99 = get_latency99('../out/osdi2020/'
                                            'ps_log_12workers_1core')
pc_ps_latency99.append(1000)
random_pc_ps_load, random_pc_ps_latency99 = get_latency99(
        '../out/osdi2020/random_ps_log_12workers_1core')
random_pc_ps_latency99.append(1000)
pc_fcfs_load, pc_fcfs_latency99 = get_latency99('../out/osdi2020/'
                                                'fcfs-eb_log_12workers_1core')
random_pc_fcfs_load, random_pc_fcfs_latency99 = get_latency99(
        '../out/osdi2020/random_fcfs-eb_log_12workers_1core')

plt.plot(lb_load, lb_latency99, marker='o', label='Late Binding',
         color='firebrick', linewidth=LINE_WIDTH, markersize=MARKER_SIZE)
plt.plot(lb_load, pc_fcfs_latency99, marker='^', color='olive',
         label='E / C / L / FCFS', linewidth=LINE_WIDTH,
         markeredgewidth=LINE_WIDTH / 2.0, markersize=MARKER_SIZE)
plt.plot(lb_load, pc_ps_latency99, marker='v', color='darkorchid',
         label='E / C / L / PS', linewidth=LINE_WIDTH,
         markeredgewidth=LINE_WIDTH / 2.0, markersize=MARKER_SIZE)
plt.plot(lb_load, random_pc_fcfs_latency99, marker='*', color='teal',
         label='E / C / R / FCFS', linewidth=LINE_WIDTH,
         markeredgewidth=LINE_WIDTH / 2.0, markersize=MARKER_SIZE)
plt.plot(lb_load, random_pc_ps_latency99, marker='s', color='blue',
         label='E / C / R / PS', linewidth=LINE_WIDTH,
         markeredgewidth=LINE_WIDTH / 2.0, markersize=MARKER_SIZE)
plt.plot(lb_load, ps_ps_latency99, marker='x', color='darkgreen',
         linewidth=LINE_WIDTH, markeredgewidth=LINE_WIDTH / 2.0,
         markersize=MARKER_SIZE, label='E / S / * / PS')

plt.xlabel('Load', fontsize=LABEL_SIZE)
plt.ylabel('99% Latency (seconds)', fontsize=LABEL_SIZE)
plt.legend(ncol=2, fontsize=LEGEND_SIZE, loc='upper left')
plt.ylim(0, 1000)
plt.xlim(0, 1)
plt.xticks(fontsize=TICK_SIZE)
plt.yticks(fontsize=TICK_SIZE)

plt.savefig('./images/p99_latency_log_1worker_12cores.png')


# Plot Lognormal Slowdown p50 -- 1 worker -- 12 cores
plt.figure(figsize=(20,15))

lb_load, lb_slowdown50 = get_slowdown50('../out/osdi2020/'
                                        'fcfs_log_1worker_12cores')
ps_ps_load, ps_ps_slowdown50 = get_slowdown50(
        '../out/osdi2020/ps_log_1worker_12cores')
ps_ps_slowdown50.append(1000)
pc_ps_load, pc_ps_slowdown50 = get_slowdown50('../out/osdi2020/'
                                              'ps_log_12workers_1core')
pc_ps_slowdown50.append(1000)
random_pc_ps_load, random_pc_ps_slowdown50 = get_slowdown50(
        '../out/osdi2020/random_ps_log_12workers_1core')
random_pc_ps_slowdown50.append(1000)
pc_fcfs_load, pc_fcfs_slowdown50 = get_slowdown50('../out/osdi2020/'
                                                'fcfs-eb_log_12workers_1core')
random_pc_fcfs_load, random_pc_fcfs_slowdown50 = get_slowdown50(
        '../out/osdi2020/random_fcfs-eb_log_12workers_1core')
random_pc_fcfs_load, random_pc_fcfs_slowdown50 = get_slowdown50(
        '../out/osdi2020/random_fcfs-eb_log_12workers_1core')

plt.plot(lb_load, lb_slowdown50, marker='o', label='Late Binding',
         color='firebrick', linewidth=LINE_WIDTH, markersize=MARKER_SIZE)
plt.plot(lb_load, pc_fcfs_slowdown50, marker='^', color='olive',
         label='E / C / L / FCFS', linewidth=LINE_WIDTH,
         markeredgewidth=LINE_WIDTH / 2.0, markersize=MARKER_SIZE)
plt.plot(lb_load, pc_ps_slowdown50, marker='v', color='darkorchid',
         label='E / C / L / PS', linewidth=LINE_WIDTH,
         markeredgewidth=LINE_WIDTH / 2.0, markersize=MARKER_SIZE)
plt.plot(lb_load, random_pc_fcfs_slowdown50, marker='*', color='teal',
         label='E / C / R / FCFS', linewidth=LINE_WIDTH,
         markeredgewidth=LINE_WIDTH / 2.0, markersize=MARKER_SIZE)
plt.plot(lb_load, random_pc_ps_slowdown50, marker='s', color='blue',
         label='E / C / R / PS', linewidth=LINE_WIDTH,
         markeredgewidth=LINE_WIDTH / 2.0, markersize=MARKER_SIZE)
plt.plot(lb_load, ps_ps_slowdown50, marker='x', color='darkgreen',
         linewidth=LINE_WIDTH, markeredgewidth=LINE_WIDTH / 2.0,
         markersize=MARKER_SIZE, label='E / S / * / PS')

plt.xlabel('Load', fontsize=LABEL_SIZE)
plt.ylabel('50% Slowdown', fontsize=LABEL_SIZE)
plt.legend(ncol=2, fontsize=LEGEND_SIZE, loc='upper left')
plt.ylim(0, 10)
plt.xlim(0, 1)
plt.xticks(fontsize=TICK_SIZE)
plt.yticks(fontsize=TICK_SIZE)
plt.savefig('./images/p50_log_1worker_12cores.png')

##########################################################################
##########################################################################
##########################################################################
##########################################################################
##########################################################################
##########################################################################

# Plot Lognormal Slowdown p99 -- 4 workers -- 12 cores
plt.figure(figsize=(20,15))

lb_load, lb_slowdown99 = get_slowdown('../out/osdi2020/'
                                      'fcfs_log_4workers_12cores')
ps_ps_load, ps_ps_slowdown99 = get_slowdown('../out/osdi2020/'
                                      'ps_log_4workers_12cores')
ps_ps_slowdown99.append(1000)
pc_ps_load, pc_ps_slowdown99 = get_slowdown('../out/osdi2020/'
                                            'ps_log_48workers_1core')
pc_ps_slowdown99.append(1000)
pc_load, pc_slowdown99 = get_slowdown('../out/osdi2020/'
                                      'fcfs-eb_log_48workers_1core')
random_ps_ps_load, random_ps_ps_slowdown99 = get_slowdown('../out/osdi2020/'
                                        'random_log_4workers_12cores')
random_ps_ps_slowdown99.append(1000)

plt.plot(lb_load, lb_slowdown99, marker='o', label='Late Binding',
         color='firebrick', linewidth=LINE_WIDTH, markersize=MARKER_SIZE)
plt.plot(lb_load, pc_ps_slowdown99, marker='v', color='darkorchid',
         label='E / C / L / PS', linewidth=LINE_WIDTH,
         markeredgewidth=LINE_WIDTH / 2.0, markersize=MARKER_SIZE)
plt.plot(lb_load, ps_ps_slowdown99, marker='x', color='darkgreen',
         linewidth=LINE_WIDTH, markeredgewidth=LINE_WIDTH / 2.0,
         markersize=MARKER_SIZE, label='E / S / L / PS')
plt.plot(lb_load, random_ps_ps_slowdown99, marker='h', color='mediumblue',
         linewidth=LINE_WIDTH, markeredgewidth=LINE_WIDTH / 2.0,
         markersize=MARKER_SIZE, label='E / S / R / PS')


plt.xlabel('Load', fontsize=LABEL_SIZE)
plt.ylabel('99% Slowdown', fontsize=LABEL_SIZE)
plt.legend(ncol=2, fontsize=LEGEND_SIZE, loc='upper left')
plt.ylim(0, 10)
plt.xlim(0, 1)
plt.xticks(fontsize=TICK_SIZE)
plt.yticks(fontsize=TICK_SIZE)
plt.savefig('./images/p99_log_4workers_12cores.png')

##########################################################################
##########################################################################
##########################################################################
##########################################################################
##########################################################################
##########################################################################

# Plot Lognormal Slowdown p99 -- 4 workers -- unbalanced
plt.figure(figsize=(20,15))

lb_load, lb_slowdown99 = get_slowdown('../out/osdi2020/'
                                      'fcfs_log_4workers_12cores')
ps_ps_load, ps_ps_slowdown99 = get_slowdown('../out/osdi2020/'
                                            'ps_log_4workers_unbalanced')
ps_ps_slowdown99.append(1000)
ps_prop_load, ps_prop_slowdown99 = get_slowdown('../out/osdi2020/ps_log_'
                                                '4workers_proportional')
ps_prop_slowdown99.append(1000)
pc_ps_load, pc_ps_slowdown99 = get_slowdown('../out/osdi2020/'
                                            'ps_log_48workers_1core')
pc_ps_slowdown99.append(1000)
random_load, random_slowdown99 = get_slowdown('../out/osdi2020/'
                                              'random_log_4workers_unbalanced')

plt.plot(lb_load, lb_slowdown99, marker='o', label='Late Binding',
         color='firebrick', linewidth=LINE_WIDTH, markersize=MARKER_SIZE)
plt.plot(lb_load, pc_ps_slowdown99, marker='v', color='darkorchid',
         label='E / C / L / PS', linewidth=LINE_WIDTH,
         markeredgewidth=LINE_WIDTH / 2.0, markersize=MARKER_SIZE)
plt.plot(lb_load, ps_ps_slowdown99, marker='x', color='darkgreen',
         linewidth=LINE_WIDTH, markeredgewidth=LINE_WIDTH / 2.0,
         markersize=MARKER_SIZE, label='E / S / L / PS')
plt.plot(random_load, random_slowdown99, marker='h', color='mediumblue',
         linewidth=LINE_WIDTH, markeredgewidth=LINE_WIDTH / 2.0,
         markersize=MARKER_SIZE, label='E / S / R / PS')
plt.plot(lb_load, ps_prop_slowdown99, marker='>', color='salmon',
         linewidth=LINE_WIDTH, markeredgewidth=LINE_WIDTH / 2.0,
         markersize=MARKER_SIZE, label='E / S / PL / PS')

plt.xlabel('Load', fontsize=LABEL_SIZE)
plt.ylabel('99% Slowdown', fontsize=LABEL_SIZE)
plt.legend(ncol=2, fontsize=LEGEND_SIZE, loc='upper left')
plt.ylim(0, 10)
plt.xlim(0, 1)
plt.xticks(fontsize=TICK_SIZE)
plt.yticks(fontsize=TICK_SIZE)
plt.savefig('./images/p99_log_4workers_unbalanced.png')
