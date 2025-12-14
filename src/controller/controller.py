import math
import random
import logging

from operator import itemgetter

from host.host import *


class Controller(object):

    workers = []

    def __init__(self, env, num_workers, num_cores, capacity, latency,
                 flow_config, histograms, opts):

        self.latency = latency
        self.env = env
        self.queue = FIFORequestQueue(env, -1, 0, flow_config)
        self.num_cores = num_cores
        self.num_workers = num_workers

        for i in range(num_workers):
            if 'core_list' in flow_config[0]:
                new_worker = GlobalQueueHost(env, self, i,
                                             flow_config[0]['core_list'][i],
                                             histograms, 0, flow_config, opts)
            else:
                new_worker = GlobalQueueHost(env, self, i, num_cores,
                                             histograms, 0, flow_config, opts)
            self.workers.append(new_worker)


class LateBindingController(Controller):

    def __init__(self, env, num_workers, num_cores, capacity, latency,
                 flow_config, histogram, opts):
        super(LateBindingController, self).__init__(env, num_workers,
                                                    num_cores, capacity,
                                                    latency, flow_config,
                                                    histogram, opts)
        if 'core_list' in flow_config[0]:
            self.worker_capacity = flow_config[0]['core_list'][:]
        else:
            self.worker_capacity = [num_cores * opts.queue_per_core] * num_workers

    def receive_request(self, request):
        logging.info('Controller: Received request %d from flow %d at %f' %
                     (request.idx, request.flow_id, self.env.now))

        # Find if there is a worker with available capacity
        worker_idx = -1
        for i in range(len(self.worker_capacity)):
            if self.worker_capacity[i] > 0:
                self.worker_capacity[i] -= 1
                worker_idx = i
                break

        # If not, enqueue and wait until one become available
        if worker_idx == -1:
            self.queue.enqueue(request)
            #print("Queue Size: {}".format(len(self.queue)))
            logging.info('LateBindingController: Enqueuing request %d from'
                         ' flow %d at %f' % (request.idx, request.flow_id,
                                             self.env.now))
            return

        # If yes, take the overhead into account and assign request for
        # execution
        self.env.process(self.assign_to_worker(request, worker_idx))

    def assign_to_worker(self, request, worker_idx):
        yield self.env.timeout(self.latency)
        logging.info('LateBindingController: Assign request %d from flow'
                     ' %d at %f to worker %d' % (request.idx,
                                                 request.flow_id,
                                                 self.env.now, worker_idx))
        self.workers[worker_idx].receive_request(request)

    def receive_completion(self, request, worker_idx):
        logging.info('LateBindingController: Received completion from request'
                     ' %d from flow %d at %f from worker %d' %
                     (request.idx, request.flow_id, self.env.now, worker_idx))
        self.worker_capacity[worker_idx] += 1
        queued_request = self.queue.dequeue()
        if queued_request:
            self.worker_capacity[worker_idx] -= 1
            self.env.process(self.assign_to_worker(queued_request, worker_idx))


class HeterogeneousLeastLoadedController(Controller):

    def __init__(self, env, num_workers, num_cores, capacity, latency,
                 flow_config, histogram, opts):
        super(HeterogeneousLeastLoadedController,
              self).__init__(env, num_workers, num_cores, capacity,
                             latency, flow_config, histogram, opts)
        self.core_list = flow_config[0]['core_list']
        self.capacity = capacity
        self.worker_loads = [0] * num_workers

    def receive_request(self, request):
        logging.info('Controller: Received request %d from flow %d at %f' %
                     (request.idx, request.flow_id, self.env.now))

        # Find least-loaded worker
        worker_idx = -1
        for i in range(len(self.core_list)):
            if self.worker_loads[i] < self.core_list[i]:
                worker_idx = i
                break

        if worker_idx == -1:
            worker_idx = self.worker_loads.index(min(self.worker_loads))

        # If we reached capacity, wait until a worker becomes available
        if worker_idx == -1:
            self.queue.enqueue(request)
            logging.info('HeterogeneousLeastLoadedController: Enqueuing'
                         'request %d from flow %d at %f' % (request.idx,
                                                            request.flow_id,
                                                            self.env.now))
            return

        # Take the overhead into account and assign request for
        # execution
        self.worker_loads[worker_idx] += 1
        self.env.process(self.assign_to_worker(request, worker_idx))

    def assign_to_worker(self, request, worker_idx):
        yield self.env.timeout(self.latency)
        logging.info('HeterogeneousLeastLoadedController: Assign request %d'
                     ' from flow %d at %f to worker %d' % (request.idx,
                                                           request.flow_id,
                                                           self.env.now,
                                                           worker_idx))
        self.workers[worker_idx].receive_request(request)

    def receive_completion(self, request, worker_idx):
        logging.info('HeterogeneousLeastLoadedController: Received completion'
                     ' from request %d from flow %d at %f from worker %d' %
                     (request.idx, request.flow_id, self.env.now, worker_idx))
        self.worker_loads[worker_idx] -= 1
        queued_request = self.queue.dequeue()
        if queued_request:
            self.worker_loads[worker_idx] += 1
            self.env.process(self.assign_to_worker(queued_request, worker_idx))


class LeastLoadedController(Controller):

    def __init__(self, env, num_workers, num_cores, capacity, latency,
                 flow_config, histogram, opts):
        super(LeastLoadedController, self).__init__(env, num_workers,
                                                    num_cores, capacity,
                                                    latency, flow_config,
                                                    histogram, opts)
        self.capacity = capacity
        self.worker_loads = [0] * num_workers

    def receive_request(self, request):
        logging.info('Controller: Received request %d from flow %d at %f' %
                     (request.idx, request.flow_id, self.env.now))

        # Find least-loaded worker
        worker_idx = self.worker_loads.index(min(self.worker_loads))
        if self.worker_loads[worker_idx] == self.capacity:
            worker_idx = -1

        # If we reached capacity, wait until a worker becomes available
        if worker_idx == -1:
            self.queue.enqueue(request)
            logging.info('LeastLoadedController: Enqueuing request %d from'
                         ' flow %d at %f' % (request.idx, request.flow_id,
                                             self.env.now))
            return

        # Take the overhead into account and assign request for
        # execution
        self.worker_loads[worker_idx] += 1
        self.env.process(self.assign_to_worker(request, worker_idx))

    def assign_to_worker(self, request, worker_idx):
        yield self.env.timeout(self.latency)
        logging.info('LeastLoadedController: Assign request %d from flow'
                     ' %d at %f to worker %d' % (request.idx,
                                                 request.flow_id,
                                                 self.env.now, worker_idx))
        self.workers[worker_idx].receive_request(request)

    def receive_completion(self, request, worker_idx):
        logging.info('LeastLoadedController: Received completion from request'
                     ' %d from flow %d at %f from worker %d' %
                     (request.idx, request.flow_id, self.env.now, worker_idx))
        self.worker_loads[worker_idx] -= 1
        queued_request = self.queue.dequeue()
        if queued_request:
            self.worker_loads[worker_idx] += 1
            self.env.process(self.assign_to_worker(queued_request, worker_idx))


class LeastLoadedSRPTController(Controller):

    def __init__(self, env, num_workers, num_cores, capacity, latency,
                 flow_config, histogram, opts):
        super(LeastLoadedSRPTController, self).__init__(env, num_workers,
                                                        num_cores, capacity,
                                                        latency, flow_config,
                                                        histogram, opts)
        self.capacity = capacity
        self.worker_loads = [0] * num_workers
        self.workers = []
        for i in range(num_workers):
            if 'core_list' in flow_config[0]:
                new_worker = SRPTQueueHost(env, self, i,
                                           flow_config[0]['core_list'][i],
                                           histogram, 0, flow_config, opts)
            else:
                new_worker = SRPTQueueHost(env, self, i, num_cores,
                                           histogram, 0, flow_config, opts)
            self.workers.append(new_worker)

    def receive_request(self, request):
        logging.info('Controller: Received request %d from flow %d at %f' %
                     (request.idx, request.flow_id, self.env.now))

        # Find least-loaded worker
        worker_idx = self.worker_loads.index(min(self.worker_loads))
        if self.worker_loads[worker_idx] == self.capacity:
            worker_idx = -1

        # If we reached capacity, wait until a worker becomes available
        if worker_idx == -1:
            self.queue.enqueue(request)
            logging.info('LeastLoadedSRPTController: Enqueuing request %d from'
                         ' flow %d at %f' % (request.idx, request.flow_id,
                                             self.env.now))
            return

        # Take the overhead into account and assign request for
        # execution
        self.worker_loads[worker_idx] += 1
        self.env.process(self.assign_to_worker(request, worker_idx))

    def assign_to_worker(self, request, worker_idx):
        yield self.env.timeout(self.latency)
        logging.info('LeastLoadedSRPTController: Assign request %d from flow'
                     ' %d at %f to worker %d' % (request.idx,
                                                 request.flow_id,
                                                 self.env.now, worker_idx))
        self.workers[worker_idx].receive_request(request)

    def receive_completion(self, request, worker_idx):
        logging.info('LeastLoadedSRPTController: Received completion from request'
                     ' %d from flow %d at %f from worker %d' %
                     (request.idx, request.flow_id, self.env.now, worker_idx))
        self.worker_loads[worker_idx] -= 1
        queued_request = self.queue.dequeue()
        if queued_request:
            self.worker_loads[worker_idx] += 1
            self.env.process(self.assign_to_worker(queued_request, worker_idx))

class ProportionalLeastLoadedController(Controller):

    def __init__(self, env, num_workers, num_cores, capacity, latency,
                 flow_config, histogram, opts):
        super(ProportionalLeastLoadedController,
              self).__init__(env, num_workers, num_cores, capacity,
                             latency, flow_config, histogram, opts)
        self.core_list = flow_config[0]['core_list']
        self.capacity = capacity
        self.worker_loads = [0] * num_workers

    def receive_request(self, request):
        logging.info('Controller: Received request %d from flow %d at %f' %
                     (request.idx, request.flow_id, self.env.now))

        # Find least-loaded worker
        worker_idx = -1
        for i in range(len(self.core_list)):
            if self.worker_loads[i] < self.core_list[i]:
                worker_idx = i
                break

        if worker_idx == -1:
            new_loads = map(lambda x: x + 1, self.worker_loads)
            prop_loads = [1.0 * a / b for a, b in zip(new_loads,
                                                      self.core_list)]
            worker_idx = min(enumerate(prop_loads), key=itemgetter(1))[0]

        # If we reached capacity, wait until a worker becomes available
        if worker_idx == -1:
            self.queue.enqueue(request)
            logging.info('ProportionalLeastLoadedController: Enqueuing request'
                         ' %d from flow %d at %f' % (request.idx,
                                                     request.flow_id,
                                                     self.env.now))
            return

        # Take the overhead into account and assign request for
        # execution
        self.worker_loads[worker_idx] += 1
        self.env.process(self.assign_to_worker(request, worker_idx))

    def assign_to_worker(self, request, worker_idx):
        yield self.env.timeout(self.latency)
        logging.info('ProportionalLeastLoadedController: Assign request %d'
                     ' from flow %d at %f to worker %d' % (request.idx,
                                                           request.flow_id,
                                                           self.env.now,
                                                           worker_idx))
        self.workers[worker_idx].receive_request(request)

    def receive_completion(self, request, worker_idx):
        logging.info('ProportionalLeastLoadedController: Received completion'
                     ' from request  %d from flow %d at %f from worker %d' %
                     (request.idx, request.flow_id, self.env.now, worker_idx))
        self.worker_loads[worker_idx] -= 1
        queued_request = self.queue.dequeue()
        if queued_request:
            self.worker_loads[worker_idx] += 1
            self.env.process(self.assign_to_worker(queued_request, worker_idx))


class LPSController(Controller):

    def __init__(self, env, num_workers, num_cores, capacity, latency,
                 flow_config, histogram, opts):
        super(LPSController, self).__init__(env, num_workers, num_cores,
                                            capacity, latency, flow_config,
                                            histogram, opts)
        self.capacity = max(num_cores, int(math.floor(1 / (1 -
            flow_config[0]['load'])) + 1))
        self.loads = [0] * num_workers

    def receive_request(self, request):
        logging.info('Controller: Received request %d from flow %d at %f' %
                     (request.idx, request.flow_id, self.env.now))

        # Find if there is a worker with available capacity
        worker_idx = -1
        for i in range(len(self.loads)):
            if self.loads[i] < self.num_cores:
                self.loads[i] += 1
                worker_idx = i
                break

        if worker_idx == -1 and min(self.loads) < self.capacity:
            worker_idx = 0
            for i in range(len(self.loads)):
                if self.loads[i] < self.loads[worker_idx]:
                    worker_idx = i
            self.loads[worker_idx] += 1

        # If not, enqueue and wait until one become available
        if worker_idx == -1:
            self.queue.enqueue(request)
            logging.info('LPSController: Enqueuing request %d from'
                         ' flow %d at %f' % (request.idx, request.flow_id,
                                             self.env.now))
            return

        # If yes, take the overhead into account and assign request for
        # execution
        self.env.process(self.assign_to_worker(request, worker_idx))

    def assign_to_worker(self, request, worker_idx):
        yield self.env.timeout(self.latency)
        logging.info('LPSController: Assign request %d from flow'
                     ' %d at %f to worker %d' % (request.idx,
                                                 request.flow_id,
                                                 self.env.now, worker_idx))
        self.workers[worker_idx].receive_request(request)

    def receive_completion(self, request, worker_idx):
        logging.info('LPSController: Received completion from request'
                     ' %d from flow %d at %f from worker %d' %
                     (request.idx, request.flow_id, self.env.now, worker_idx))
        self.loads[worker_idx] -= 1
        queued_request = self.queue.dequeue()
        if queued_request:
            self.loads[worker_idx] += 1
            self.env.process(self.assign_to_worker(queued_request, worker_idx))


class RandomController(Controller):

    def __init__(self, env, num_workers, num_cores, capacity, latency,
                 flow_config, histogram, opts):
        super(RandomController, self).__init__(env, num_workers, num_cores,
                                               capacity, latency, flow_config,
                                               histogram, opts)

    def receive_request(self, request):
        logging.info('Controller: Received request %d from flow %d at %f' %
                     (request.idx, request.flow_id, self.env.now))

        # Choose a random worker.
        worker_idx = random.randint(0, self.num_workers - 1)

        # Take the overhead into account and assign request for
        # execution
        self.env.process(self.assign_to_worker(request, worker_idx))

    def assign_to_worker(self, request, worker_idx):
        yield self.env.timeout(self.latency)
        logging.info('RandomController: Assign request %d from flow'
                     ' %d at %f to worker %d' % (request.idx,
                                                 request.flow_id,
                                                 self.env.now, worker_idx))
        self.workers[worker_idx].receive_request(request)

    def receive_completion(self, request, worker_idx):
        logging.info('RandomController: Received completion from request'
                     ' %d from flow %d at %f from worker %d' %
                     (request.idx, request.flow_id, self.env.now, worker_idx))


class LocalityController(Controller):

    def __init__(self, env, num_workers, num_cores, capacity, latency,
                 flow_config, histogram, opts):
        super(LocalityController, self).__init__(env, num_workers,
                                                 num_cores, capacity,
                                                 latency, flow_config,
                                                 histogram, opts)
        self.worker_capacity = [capacity] * num_workers

    def receive_request(self, request):
        logging.info('LocalityController: Received request %d from flow %d at %f' %
                     (request.idx, request.flow_id, self.env.now))

        # Find if there is a worker with available capacity
        worker_idx = -1
        worker_idx = request.idx % len(self.worker_capacity)
        if self.worker_capacity[worker_idx] < 1:
            worker_idx = random.randint(0, len(self.worker_capacity) - 1)

        self.worker_capacity[worker_idx] -= 1

        # If yes, take the overhead into account and assign request for
        # execution
        self.env.process(self.assign_to_worker(request, worker_idx))

    def assign_to_worker(self, request, worker_idx):
        yield self.env.timeout(self.latency)
        logging.info('LocalityController: Assign request %d from flow'
                     ' %d at %f to worker %d' % (request.idx,
                                                 request.flow_id,
                                                 self.env.now, worker_idx))
        self.workers[worker_idx].receive_request(request)

    def receive_completion(self, request, worker_idx):
        logging.info('LocalityController: Received completion from request'
                     ' %d from flow %d at %f from worker %d' %
                     (request.idx, request.flow_id, self.env.now, worker_idx))
        self.worker_capacity[worker_idx] += 1
        queued_request = self.queue.dequeue()
        if queued_request:
            self.worker_capacity[worker_idx] -= 1
            self.env.process(self.assign_to_worker(queued_request, worker_idx))
