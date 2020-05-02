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

OUTPUT_DIR = "../out/spring2020/lb_4workers_12cores/"

def main():
    global OUTPUT_DIR
    # Set the simulation parameters
    iterations = 1
    core_count = [1]
    worker_count = [48]
    latencies = [0, 0.2]
    capacities = [2]

    cores_to_run = 24
    batch_run = math.ceil(float(cores_to_run) / iterations)

    # Sanity check
    if not OUTPUT_DIR.endswith("/"):
        OUTPUT_DIR += "/"

    # Create folder if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    config_jsons = []
    default_json = [{
        "work_gen": "lognormal_request",
        "inter_gen": "poisson_arrival",
        "mean": -0.38,
        "std_dev_request": 2.36,
        "rps": 1.0,
        "time_slice": 0.5,
        "preemption": 0.0,
        "enq_front": False
        }]

    rps = [1, 2, 3, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4,
           4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 5,
           5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 6, 7, 8]
    for i in rps:
        temp_conf = copy.deepcopy(default_json)
        temp_conf[0]["rps"] = i
        config_jsons.append(temp_conf)

    seeds = [1000]

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
        output.append(q.get()[0])

    print("RPS")
    for val in rps:
        print(val)

    for latency in latencies:
        filtered = filter(lambda elem: elem['latency'] == latency, output)
        filtered = sorted(filtered, key = lambda elem: elem['rps'])
        print('THROUGHPUT FOR OVERHEAD: ' + str(latency))
        for elem in filtered:
            print(str(elem['total_throughput']))

    for latency in latencies:
        filtered = filter(lambda elem: elem['latency'] == latency, output)
        filtered = sorted(filtered, key = lambda elem: elem['rps'])
        print('AVG EXEC TIME FOR OVERHEAD: ' + str(latency))
        for elem in filtered:
            print(str(elem['avg_exec_time']))

    for latency in latencies:
        filtered = filter(lambda elem: elem['latency'] == latency, output)
        filtered = sorted(filtered, key = lambda elem: elem['rps'])
        print('P50 LATENCY FOR OVERHEAD: ' + str(latency))
        for elem in filtered:
            print(str(elem['latency50']))

    for latency in latencies:
        filtered = filter(lambda elem: elem['latency'] == latency, output)
        filtered = sorted(filtered, key = lambda elem: elem['rps'])
        print('P90 LATENCY FOR OVERHEAD: ' + str(latency))
        for elem in filtered:
            print(str(elem['latency90']))

    for latency in latencies:
        filtered = filter(lambda elem: elem['latency'] == latency, output)
        filtered = sorted(filtered, key = lambda elem: elem['rps'])
        print('P99 LATENCY FOR OVERHEAD: ' + str(latency))
        for elem in filtered:
            print(str(elem['latency99']))

    for latency in latencies:
        filtered = filter(lambda elem: elem['latency'] == latency, output)
        filtered = sorted(filtered, key = lambda elem: elem['rps'])
        print('P50 SLOWDOWN FOR OVERHEAD: ' + str(latency))
        for elem in filtered:
            print(str(elem['slowdown50']))

    for latency in latencies:
        filtered = filter(lambda elem: elem['latency'] == latency, output)
        filtered = sorted(filtered, key = lambda elem: elem['rps'])
        print('P90 SLOWDOWN FOR OVERHEAD: ' + str(latency))
        for elem in filtered:
            print(str(elem['slowdown90']))

    for latency in latencies:
        filtered = filter(lambda elem: elem['latency'] == latency, output)
        filtered = sorted(filtered, key = lambda elem: elem['rps'])
        print('P99 SLOWDOWN FOR OVERHEAD: ' + str(latency))
        for elem in filtered:
            print(str(elem['slowdown99']))


def run_sim(latency, workers, cores, cap, config_json, iterations, seeds, q):
    # Create config file
    conf, config_file = tempfile.mkstemp()
    os.write(conf, json.dumps(config_json))
    os.close(conf)

    # Run the simulation
    sim_args = ["../src/sim.py",
                "--cores", str(cores),
                "--workers", str(workers),
                "--workload-conf", str(config_file),
                "--latency", str(latency),
                "--capacity", str(cap)]

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

    for p in running_jobs:
        out, err = p.communicate()
        output = json.loads(out)
        for i in range(len(config_json)):
            output[i]['rps'] = config_json[i]['rps']
            output[i]['cores'] = cores
            output[i]['workers'] = workers
            output[i]['cap'] = cap
            output[i]['latency'] = latency
        q.put(output)
    #
    #    for i in range(len(config_json)):
    #        per_flow_latency[i].append(output[i]['latency'])
    #        per_flow_throughput[i].append(output[i]['per_core_through'])
    #        per_flow_slo[i].append(output[i]['slo_success'])

    try:
        os.remove(config_file)
    except:
        pass
    # Gather the results
    #output_name = (OUTPUT_DIR + "sim_" + str(cores) + "_" + str(host) + "_" +
    #               str(deq_cost) + "_" + queue_policy)
    #full_name = output_name
    #for key in range(len(config_json)):
    #    val = config_json[key]
    #    flow_name = ("_" + "flow" + str(key) + "_" + str(val["work_gen"]) +
    #                 "_" + str(val["inter_gen"]) + "_" + str(val["load"]))

    #    if val.get("mean") is not None:
    #        flow_name += "_" + str(val["mean"])
    #    if val.get("std_dev_request") is not None:
    #        flow_name += "_" + str(val["std_dev_request"])
    #    if val.get("exec_time") is not None:
    #        flow_name += "_" + str(val["exec_time"])
    #    if val.get("heavy_per") is not None:
    #        flow_name += "_" + str(val["heavy_per"])
    #    if val.get("heavy_time") is not None:
    #        flow_name += "_" + str(val["heavy_time"])
    #    if val.get("std_dev_arrival") is not None:
    #        flow_name += "_" + str(val["std_dev_arrival"])
    #    if val.get("time_slice") is not None:
    #        flow_name += "_" + str(val["time_slice"])
    #    if val.get("enq_front") is not None:
    #        flow_name += "_enqfront" + str(val["enq_front"])

    #    full_name += flow_name

    #for i in range(len(config_json)):
    #    flow_name = "_" + "flow" + str(i)
    #    flow_name = full_name + flow_name
    #    with open(flow_name, 'w') as f:
    #        for value in per_flow_latency[i]:
    #            f.write(str(value) + "\n")

    #    flow_name = flow_name + ".total"
    #    with open(flow_name, 'w') as f:
    #        value = sum(per_flow_latency[i]) * 1.0 / len(per_flow_latency[i])
    #        f.write(str(value) + "\n")

    #    flow_name = "_" + "flow" + str(i)
    #    flow_name = full_name + flow_name + '.throughput'
    #    with open(flow_name, 'w') as f:
    #        for value in per_flow_throughput[i]:
    #            f.write(str(value) + "\n")

    #    flow_name = flow_name + ".total"
    #    with open(flow_name, 'w') as f:
    #        value = (sum(per_flow_throughput[i]) * 1.0 /
    #                 len(per_flow_throughput[i]))
    #        f.write(str(value) + "\n")

    #    flow_name = "_" + "flow" + str(i)
    #    flow_name = full_name + flow_name + '.slo'
    #    with open(flow_name, 'w') as f:
    #        for value in per_flow_slo[i]:
    #            f.write(str(value) + "\n")

    #    flow_name = flow_name + ".total"
    #    with open(flow_name, 'w') as f:
    #        value = (sum(per_flow_slo[i]) * 1.0 /
    #                 len(per_flow_slo[i]))
    #        f.write(str(value) + "\n")

    ## Delete config file
    #try:
    #    os.remove(config_file)
    #except:
    #    pass


if __name__ == "__main__":
    main()
