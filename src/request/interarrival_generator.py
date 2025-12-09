import numpy as np


class InterArrivalGenerator(object):
    def __init__(self, mean, opts=None):
        self.mean = mean

    def next(self):
        return 1


class PoissonArrivalGenerator(InterArrivalGenerator):
    def next(self):
        return np.random.exponential(self.mean)


class LogNormalArrivalGenerator(InterArrivalGenerator):
    def __init__(self, mean, opts=None):
        InterArrivalGenerator.__init__(self, mean, opts)
        self.scale = float(opts["std_dev_arrival"]**2)
        # Calculate the mean of the underlying normal distribution
        self.mean = np.log(mean**2 / np.sqrt(mean**2 + self.scale))
        self.scale = np.sqrt(np.log(self.scale / mean**2 + 1))

    def next(self):
        return np.random.lognormal(self.mean, self.scale)

class BurstyArrivalGenerator(InterArrivalGenerator):
    def __init__(self, mean, opts):
        self.idx = 0
        self.burst_count = opts.get("burst_count", 100)
        self.rate = opts.get("req_per_sec", 5)
        self.delay = opts.get("delay", 20)

    def next(self):
        base = self.delay if self.idx % self.burst_count == 0 else 0
        self.idx += 1
        return base + (1 / self.rate)

class TrickleArrivalGenerator(InterArrivalGenerator):
    def __init__(self, mean, opts):
        self.rate = opts.get("num_req", 10)
        self.span = opts.get("req_span", 60)

    def next(self):
        return self.span / self.rate

