import math
import random
from request.request import Request
import numpy as np

class RequestGenerator(object):

    flow_id = 1

    def __init__(self, env, host, load, num_cores):
        self.env = env
        self.host = host
        self.load = load
        self.num_cores = num_cores
        self.action = None

    def set_host(self, host):
        self.host = host

    def begin_generation(self):
        self.action = self.env.process(self.run())

    def set_flow_id(self, flow_id):
        self.flow_id = flow_id

    def run(self):
        idx = 0
        while True:
            # Fixed 7 execution time
            self.host.receive_request(Request(idx, 7,
                                              self.env.now,
                                              self.flow_id))
            yield self.env.timeout(1)
            idx += 1


class MultipleRequestGenerator(object):
    def __init__(self, env, host):
        self.env = env
        self.host = host
        self.generators = []
        self.cur_flow_id = 0
        self.idx = 0

    def add_generator(self, gen):
        gen.set_flow_id(self.cur_flow_id)
        self.cur_flow_id += 1
        self.generators.append(gen)

    def begin_generation(self):
        for i in self.generators:
            i.set_host(self)
            i.begin_generation()

    def receive_request(self, request):
        request.idx = self.idx
        self.host.receive_request(request)
        self.idx += 1


class HeavyTailRequestGenerator(RequestGenerator):
    def __init__(self, hist, env, host, inter_gen, num_cores, opts):
        # Tail percent of 2 means that 2% of requests require "tail latency"
        # execution time, the others require "latency" execution
        # time.
        RequestGenerator.__init__(self, env, host, opts["load"], num_cores)
        self.exec_time = opts["exec_time"]
        self.heavy_exec_time = opts["heavy_time"]
        self.heavy_percent = opts["heavy_per"]
        self.hist = hist
        self.mean = (self.heavy_exec_time * (self.heavy_percent / 100.0) +
                     self.exec_time * ((100 - self.heavy_percent) / 100.0))
        inv_load = 1.0 / self.load
        mean = inv_load * self.mean / self.num_cores
        self.inter_gen = inter_gen(mean, opts)
        if opts.has_key("request_types"):
            self.request_types = opts["request_types"]
        else:
            self.request_types = 0

    def run(self):
        idx = 0
        while True:
            # Generate inter-arrival time
            s = self.inter_gen.next()
            yield self.env.timeout(s)
            self.hist.add_request()

            # Generate request
            # NOTE Percentage must be integer
            is_heavy = random.randint(0, 999) < self.heavy_percent * 10
            exec_time = self.heavy_exec_time if is_heavy else self.exec_time

            if self.request_types > 0:
                if random.randInt(0, 99) < 98:
                    idx = 0
                else:
                    idx = random.randInt(1,49)

            self.host.receive_request(Request(idx, exec_time, self.env.now,
                                              self.flow_id, self.mean))

            idx += 1


class ExponentialRequestGenerator(RequestGenerator):
    def __init__(self, hist, env, host, inter_gen, num_cores, opts):
        RequestGenerator.__init__(self, env, host, opts["load"], num_cores)
        self.mean = float(opts["mean"])
        self.hist = hist
        arrival_mean = self.mean / self.load / self.num_cores
        self.inter_gen = inter_gen(arrival_mean, opts)

    def run(self):
        idx = 0
        while True:

            # Generate inter-arrival time
            s = self.inter_gen.next()
            yield self.env.timeout(s)
            self.hist.add_request()
            exec_time = np.random.exponential(self.mean)

            self.host.receive_request(Request(idx, exec_time, self.env.now,
                                              self.flow_id, self.mean))

            idx += 1


class LogNormalRequestGenerator(RequestGenerator):
    def __init__(self, hist, env, host, inter_gen, num_cores, opts):
        RequestGenerator.__init__(self, env, host, opts["load"], num_cores)

        self.mean = opts["mean"]
        self.std = opts["std_dev_request"]
        self.hist = hist

        self.log_mean = math.exp(self.mean + (self.std * self.std) / 2)
        arrival_mean = self.log_mean / self.load / self.num_cores

        self.inter_gen = inter_gen(arrival_mean, opts)

    def run(self):
        idx = 0
        while True:

            # Generate inter-arrival time
            s = self.inter_gen.next()
            yield self.env.timeout(s)
            self.hist.add_request()
            exec_time = np.random.lognormal(self.mean, self.std)

            self.host.receive_request(Request(idx, exec_time, self.env.now,
                                              self.flow_id, self.log_mean))
            idx += 1


class ParetoRequestGenerator(RequestGenerator):
    def __init__(self, hist, env, host, inter_gen, num_cores, opts):
        RequestGenerator.__init__(self, env, host, opts["load"], num_cores)

        self.scale = 1 + np.sqrt(1.0 + opts["mean"]**2 /
                                 opts["std_dev_request"]**2)
        self.mu = (self.scale - 1) * opts["mean"] / self.scale

        arrival_mean = opts["mean"] / self.load / self.num_cores

        self.hist = hist
        self.inter_gen = inter_gen(arrival_mean, opts)
        self.mean = opts["mean"]

    def run(self):
        idx = 0
        while True:
            # Generate inter-arrival time
            s = self.inter_gen.next()
            yield self.env.timeout(s)

            self.hist.add_request()
            exec_time = (np.random.pareto(self.scale) + 1) * self.mu
            self.host.receive_request(Request(idx, exec_time, self.env.now,
                                              self.flow_id, self.mean))
            idx += 1


class NormalRequestGenerator(RequestGenerator):
    def __init__(self, hist, env, host, inter_gen, num_cores, opts):
        RequestGenerator.__init__(self, env, host, opts["load"], num_cores)

        self.mu = opts["mean"]
        self.std = opts["std_dev_request"]
        self.inter_gen = inter_gen(opts["mean"] / self.load / self.num_cores,
                                   opts)
        self.mean = opts["mean"]

    def run(self):
        idx = 0
        while True:
            # Generate inter-arrival time
            s = self.inter_gen.next()
            yield self.env.timeout(s)

            self.hist.add_request()
            exec_time = -1
            while (exec_time < 0 or exec_time > 2 * self.mu):
                exec_time = np.random.normal(self.mu, self.std)

            self.host.receive_request(Request(idx, exec_time, self.env.now,
                                              self.flow_id, self.mean))
            idx += 1
