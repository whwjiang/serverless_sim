import logging

from host.host import *


class Controller(object):

    workers = []

    def __init__(self, env, num_workers, num_cores, latency, flow_config,
                 histograms, opts):

        self.latency = latency
        self.env = env
        self.queue = FIFORequestQueue(env, -1, 0, flow_config)

        for i in range(num_workers):
            new_worker = GlobalQueueHost(env, self, i, num_cores,
                                         histograms, 0, flow_config, opts)
            self.workers.append(new_worker)


class LateBindingController(Controller):

    def __init__(self, env, num_workers, num_cores, latency, flow_config,
                 histogram, opts, worker_capacity=12):
        super(LateBindingController, self).__init__(env, num_workers,
                                                    num_cores, latency,
                                                    flow_config, histogram,
                                                    opts)
        self.worker_capacity = [worker_capacity] * num_workers

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
