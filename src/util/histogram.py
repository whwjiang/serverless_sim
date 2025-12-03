#!/usr/bin/env python3

import json
import logging
from hdrh.histogram import HdrHistogram

class EndException(Exception):
    pass

class Histogram(object):

    def __init__(self, env, time, num_histograms, cores, flow_config, opts):
        self.histograms = [HdrHistogram(1, 60 * 60 * 1000, 2)
                           for i in range(num_histograms)]
        self.slowdowns = [HdrHistogram(1, 60 * 60 * 1000, 2)
                          for i in range(num_histograms)]
        self.global_histogram = HdrHistogram(1, 60 * 60 * 1000, 2)
        self.cores = cores
        self.flow_config = flow_config
        self.exec_time = [0 for i in range(len(flow_config))]
        self.latency = [0 for i in range(len(flow_config))]
        self.slowdown = [0 for i in range(len(flow_config))]
        self.violations = [0 for i in range(len(flow_config))]
        self.dropped = [0 for i in range(len(flow_config))]
        self.completed = [0 for i in range(len(flow_config))]
        self.print_values = opts.print_values
        self.time = time
        self.window_start = opts.window
        self.env = env
        self.active_requests = 0
        if self.print_values:
            self.print_files = [open(opts.output_file + '_flow' + str(flow),
                                     'w+') for flow in range(len(flow_config))]

    def add_request(self):
        # Do not record values the region of interest
        if self.env.now < self.window_start or self.env.now > 2 * self.time:
            return
        self.active_requests += 1

    def record_value(self, flow, value, exec_time, start_time):
        if self.active_requests == 0 and self.env.now > 2 * self.time:
            raise EndException
        if self.env.now > 1000 * self.time:
            raise EndException
        # Do not record values the region of interest
        if start_time < self.window_start or start_time > 2 * self.time:
            return

        self.global_histogram.record_value(1000.0 * value)
        self.histograms[flow].record_value(1000.0 * value)
        self.slowdowns[flow].record_value(1000.0 * value / exec_time)
        self.latency[flow] += 1000.0 * value
        self.slowdown[flow] += 1000.0 * value / exec_time
        self.exec_time[flow] += exec_time
        self.completed[flow] += 1
        if self.flow_config[flow].get('slo'):
            if value > self.flow_config[flow].get('slo'):
                self.violations[flow] += 1
        if self.print_values:
            self.print_files[flow].write(str(value) + '\n')

        # Exit if all requests within the region of interest are served
        self.active_requests -= 1

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

            # Get average latency
            latency_avg = self.latency[i] / total_count if total_count > 0 else 0.0

            # Get the 50%-90%-99% slowdown
            slowdown50 = self.slowdowns[i].get_value_at_percentile(50)
            slowdown90 = self.slowdowns[i].get_value_at_percentile(90)
            slowdown99 = self.slowdowns[i].get_value_at_percentile(99)

            # Get average slowdown
            slowdown_avg = self.slowdown[i] / total_count if total_count > 0 else 0.0

            # Prepare the json for output
            new_value = {
                'avg_exec_time': (1.0 * self.exec_time[i] / total_count) if total_count > 0 else 0.0,
                'latency50': latency50 / 1000.0,
                'latency90': latency90 / 1000.0,
                'latency99': latency99 / 1000.0,
                'latency_avg': latency_avg / 1000.0,
                'slowdown50': slowdown50 / 1000.0,
                'slowdown90': slowdown90 / 1000.0,
                'slowdown99': slowdown99 / 1000.0,
                'slowdown_avg': slowdown_avg / 1000.0,
                'total_throughput': 1.0 * self.completed[i] / self.time,
                'total_completed': self.completed[i],
                'slo_success': 1.0 - (1.0 * self.violations[i] / total_count) if total_count > 0 else 0.0,
                'dropped_requests': self.dropped[i]
            }
            info.append(new_value)
        logging.debug('Active requests %d' % (self.active_requests))
        print(json.dumps(info))

    def drop_request(self, flow_id):
        self.dropped[flow_id] += 1
        self.violations[flow_id] += 1
