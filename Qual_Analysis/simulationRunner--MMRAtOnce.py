from qual_analysis.mmr import *
import numpy as np
import pandas as pd
import pickle
import random
import time
import click

random.seed(34)


def getTasks(fileName, numberOfTasks):
    """fileName: Name of file containing the tasks"""
    """numberOFTasks: How many tasks you need"""
    tasks = pickle.load(open(fileName, 'rb'))
    task_output = random.sample(list(tasks), numberOfTasks)
    taskOutput = {}
    for i, x in enumerate(task_output):
        taskOutput[i] = tasks[x]
    return taskOutput


def getCTTasks(fileName, numberOfTasks):
    """Get normalized tasks in CT format"""
    tasks = pickle.load(open(fileName, 'rb'))
    taskOutput = {}
    for i in range(numberOfTasks):
        taskOutput[i + 1] = tasks[i]
    return taskOutput


def intra(grouping, tasks):
    out = 0
    for g in grouping:
        g_m = np.mean([tasks[i][0] for i in g])
        out += sum([(tasks[i][0] - g_m) ** 2 for i in g])
    return out


def inter(grouping, tasks):
    out = []
    for g in grouping:
        out.append(np.mean([tasks[i][1] for i in g]))
    o = 0
    for i in range(len(out) - 1):
        o += np.fabs(out[i] - out[i + 1])
    return o


def writeResults(fileName, message):
    """Writes the results to a txt file"""
    f = open(fileName, 'a')
    f.write('\n')
    f.write(message)
    f.close()


def InterIntraChoice(i):
    if (i == 'min'):
        return min
    if (i == 'max'):
        return max


@click.command()
@click.option('--dist', prompt='Which distribution',
              type=click.Choice(['d3_tempo_loudness',
                                 'd2_release_artist_familiarity',
                                 'd1_duration_hotness']))  
@click.option('--n', prompt='Number Of Tasks(N)', type=click.INT)
@click.option('--k', prompt='K', type=click.INT)
# Runs all 4 at once

def run_mmr(n, k, dist):
    x_times = 2
    L = n // k
    o_tasks = getTasks("./data/"+str(dist) + '.p', n)  # Changed for songs

    pd_res = {}

    oInter = 0
    oIntra = 0
    runTime = []
    for i in range(x_times):
        start = time.time()
        g = mmr_new_fast(o_tasks, k, L, 0.9, 0.1, min, min)
        runTime.append(time.time() - start)
        oInter += inter(grouping=g, tasks=o_tasks)
        oIntra += intra(grouping=g, tasks=o_tasks)
    pd_res["min_min"] = [oIntra / x_times, oInter / x_times, np.mean(runTime)]

    oInter = 0
    oIntra = 0
    runTime = []
    for i in range(x_times):
        start = time.time()
        g = mmr_new_fast(o_tasks, k, L, 0.9, 0.1, min, max)
        runTime.append(time.time() - start)
        oInter += inter(grouping=g, tasks=o_tasks)
        oIntra += intra(grouping=g, tasks=o_tasks)
    pd_res["min_max"] = [oIntra / x_times, oInter / x_times, np.mean(runTime)]

    oInter = 0
    oIntra = 0
    runTime = []
    for i in range(x_times):
        start = time.time()
        g = mmr_new_fast(o_tasks, k, L, 0.9, 0.1, max, max)
        runTime.append(time.time() - start)
        oInter += inter(grouping=g, tasks=o_tasks)
        oIntra += intra(grouping=g, tasks=o_tasks)
    pd_res["max_max"] = [oIntra / x_times, oInter / x_times, np.mean(runTime)]

    oInter = 0
    oIntra = 0
    runTime = []
    for i in range(x_times):
        start = time.time()
        g = mmr_new_fast(o_tasks, k, L, 0.9, 0.1, max, min)
        runTime.append(time.time() - start)
        oInter += inter(grouping=g, tasks=o_tasks)
        oIntra += intra(grouping=g, tasks=o_tasks)
    pd_res["max_min"] = [oIntra / x_times, oInter / x_times, np.mean(runTime)]

    output = pd.DataFrame.from_dict(pd_res, orient='index', columns=["intra_score", "inter_score", "running_time"])
    output.to_csv(f"./res/mmr/mmr_alg_{n}_{k}.csv")

if __name__ == '__main__':
    run_mmr()