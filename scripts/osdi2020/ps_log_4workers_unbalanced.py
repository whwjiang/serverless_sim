#!/usr/bin/env python

import os
import copy
import json
import time
import math
import random
import tempfile
import subprocess

from multiprocessing import Process, Queue

OUTPUT_FILE = "../../out/osdi2020/ps_log_4workers_unbalanced"


def dict_mean(dict_list):
    mean_dict = {}
    for key in dict_list[0].keys():
        mean_dict[key] = sum(d[key] for d in dict_list) / len(dict_list)
    return mean_dict


def main():
    global OUTPUT_DIR
    # Set the simulation parameters
    iterations = 10
    core_count = [12]
    worker_count = [4]
    latencies = [0]
    capacities = [1000000]

    cores_to_run = 24
    batch_run = math.ceil(float(cores_to_run) / iterations)

    config_jsons = []
    default_json = [{
        "work_gen": "lognormal_request",
        "inter_gen": "poisson_arrival",
        "mean": -0.38,
        "std_dev_request": 2.36,
        "load": 0.1,
        "time_slice": 0.5,
        "preemption": 0.0,
        "enq_front": False,
        'core_list': [2, 22, 2, 22],
        }]

    loads = [0.05 * i for i in range(1,20)] + [0.96, 0.97, 0.98, 0.99]
    for i in loads:
        temp_conf = copy.deepcopy(default_json)
        temp_conf[0]["load"] = i
        config_jsons.append(temp_conf)

    seeds = [1000, 1001, 1002, 1003, 1004, 1005,
             1006, 1007, 1008, 1009]

    q = Queue()
    idle = []
    running = []
    for latency in latencies:
        for cap in capacities:
            for workers in worker_count:
                for cores in core_count:
                    for config_json in config_jsons:
                        p = Process(target=run_sim, args=(latency, workers,
                                                          cores, cap,
                                                          config_json,
                                                          iterations, seeds,
                                                          q))
                        idle.append(p)

    # Running phase
    while len(idle) > 0:
        while len(running) < batch_run and len(idle) > 0:
            p = idle.pop(0)
            p.start()
            running.append(p)
        to_finish = []
        for process in running:
            if not process.is_alive():
                to_finish.append(process)
        for p in to_finish:
            running.remove(p)
        time.sleep(1)

    print "Winding down"

    # Wind down phase
    for run in running:
        run.join()

    output = []
    while not q.empty():
        output.append(q.get())

    with open(OUTPUT_FILE, 'w+') as f:
        f.write(json.dumps(output))


def run_sim(latency, workers, cores, cap, config_json, iterations, seeds, q):
    # Create config file
    conf, config_file = tempfile.mkstemp()
    os.write(conf, json.dumps(config_json))
    os.close(conf)

    # Run the simulation
    sim_args = ["../../src/sim.py",
                "--cores", str(cores),
                "--workers", str(workers),
                "--workload-conf", str(config_file),
                "--latency", str(latency),
                "--capacity", str(cap),
                "--capacity", str(cap),
                "--controller-type", "heterogeneousll",
                "-t", str(3600)]

    per_flow_throughput = []
    per_flow_latency = []
    per_flow_slo = []
    for i in range(len(config_json)):
        per_flow_latency.append([])
        per_flow_throughput.append([])
        per_flow_slo.append([])

    running_jobs = []
    for i in range(iterations):
        arg = copy.deepcopy(sim_args)
        arg.extend(["-s", str(seeds[i])])
        p = subprocess.Popen(arg, stdout=subprocess.PIPE)
        running_jobs.append(p)

    outputs = []
    for p in running_jobs:
        out, err = p.communicate()
        output =json.loads(out)[0]
        output['load'] = config_json[0]['load']
        output['cores'] = cores
        output['workers'] = workers
        output['cap'] = cap
        output['latency'] = latency
        outputs.append(output)

    avg_output = dict_mean(outputs)
    q.put(avg_output)

    try:
        os.remove(config_file)
    except:
        pass


if __name__ == "__main__":
    main()
