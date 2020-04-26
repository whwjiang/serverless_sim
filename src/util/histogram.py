#!/usr/bin/env python

import json
from hdrh.histogram import HdrHistogram


class Histogram(object):

    def __init__(self, time, num_histograms, cores, flow_config, opts):
        self.histograms = [HdrHistogram(1, 60 * 60 * 1000, 2)
                           for i in range(num_histograms)]
        self.slowdowns = [HdrHistogram(1, 60 * 60 * 1000, 2)
                          for i in range(num_histograms)]
        self.global_histogram = HdrHistogram(1, 60 * 60 * 1000, 2)
        self.cores = cores
        self.flow_config = flow_config
        self.exec_time = [0 for i in range(len(flow_config))]
        self.violations = [0 for i in range(len(flow_config))]
        self.dropped = [0 for i in range(len(flow_config))]
        self.completed = [0 for i in range(len(flow_config))]
        self.print_values = opts.print_values
        self.time = time
        if self.print_values:
            self.print_files = [open(opts.output_file + '_flow' + str(flow),
                                     'w+') for flow in range(len(flow_config))]

    def record_value(self, flow, value, exec_time):
        self.global_histogram.record_value(1000.0 * value)
        self.histograms[flow].record_value(1000.0 * value)
        self.slowdowns[flow].record_value(1000.0 * value / exec_time)
        self.exec_time[flow] += exec_time
        self.completed[flow] += 1
        if self.flow_config[flow].get('slo'):
            if value > self.flow_config[flow].get('slo'):
                self.violations[flow] += 1
        if self.print_values:
            self.print_files[flow].write(str(value) + '\n')

    def print_info(self):
        info = []
        for i in range(len(self.histograms)):
            # Add the dropped requests as max time
            max_value = self.histograms[i].get_max_value()
            for j in range(self.dropped[i]):
                self.histograms[i].record_value(max_value)

            # Get the total count of received requests
            total_count = self.histograms[i].get_total_count()

            # Get the 50%-90%-99% latency
            latency50 = self.histograms[i].get_value_at_percentile(50)
            latency90 = self.histograms[i].get_value_at_percentile(90)
            latency99 = self.histograms[i].get_value_at_percentile(99)

            # Get the 50%-90%-99% slowdown
            slowdown50 = self.slowdowns[i].get_value_at_percentile(50)
            slowdown90 = self.slowdowns[i].get_value_at_percentile(90)
            slowdown99 = self.slowdowns[i].get_value_at_percentile(99)

            # Prepare the json for output
            new_value = {
                'avg_exec_time': (1.0 * self.exec_time[i] /
                self.histograms[i].get_total_count()),
                'latency50': latency50 / 1000.0,
                'latency90': latency90 / 1000.0,
                'latency99': latency99 / 1000.0,
                'slowdown50': slowdown50 / 1000.0,
                'slowdown90': slowdown90 / 1000.0,
                'slowdown99': slowdown99 / 1000.0,
                'total_throughput': 1.0 * self.completed[i] / self.time,
                'slo_success': 1.0 - (1.0 * self.violations[i] / total_count),
                'dropped_requests': self.dropped[i]
            }
            info.append(new_value)
        print json.dumps(info)

    def drop_request(self, flow_id):
        self.dropped[flow_id] += 1
        self.violations[flow_id] += 1
