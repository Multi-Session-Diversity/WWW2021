from qual_analysis.algs import *
import pickle
import click
import random
import pandas as pd
import time
import datetime
#import tqdm

random.seed(34)


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


def getTasks(fileName, numberOfTasks):
    """fileName: Name of file containing the tasks"""
    """numberOFTasks: How many tasks you need"""
    tasks = pickle.load(open(fileName, 'rb'))
    task_output = random.sample(list(tasks), numberOfTasks)
    taskOutput = {}
    for i, x in enumerate(task_output):
        taskOutput[i] = tasks[x]
    return taskOutput


def writeResults(fileName, message):
    """Writes the results to a txt file"""
    f = open(fileName, 'a')
    f.write('\n')
    f.write(message)
    f.close()



@click.command()
@click.option('--dist', prompt='Which distribution',
              type=click.Choice(['d3_tempo_loudness',
                                 'd2_release_artist_familiarity',
                                 'd1_duration_hotness'])) 
@click.option('--n', prompt='Number Of Tasks(N)', type=click.INT)
@click.option('--k', prompt='K', type=click.INT)
# Runs all 4 at once


def simRunOurAlg(n, k, dist):
    L = n // k
    o_tasks = getTasks("./data/"+str(dist) + '.p', n)
    pd_res = {}

    oInter = 0
    oIntra = 0
    runTime = []
    for i in range(5):
        start = time.time()
        g = min_intra_min_inter(tasks=o_tasks, k=k, l=L)
        runTime.append(time.time() - start)
        oInter += inter(grouping=g, tasks=o_tasks)
        oIntra += intra(grouping=g, tasks=o_tasks)
    pd_res["min_min"] = [oIntra / 5, oInter / 5, np.mean(runTime)]

    oInter = 0
    oIntra = 0
    runTime = []
    for i in range(5):
        start = time.time()
        g = min_intra_max_inter(tasks=o_tasks, k=k, l=L)
        runTime.append(time.time() - start)
        oInter += inter(grouping=g, tasks=o_tasks)
        oIntra += intra(grouping=g, tasks=o_tasks)
    pd_res["min_max"] = [oIntra / 5, oInter / 5, np.mean(runTime)]

    oInter = 0
    oIntra = 0
    runTime = []
    for i in range(5):
        start = time.time()
        g = max_intra_max_inter(tasks=o_tasks, k=k, l=L)
        runTime.append(time.time() - start)
        oInter += inter(grouping=g, tasks=o_tasks)
        oIntra += intra(grouping=g, tasks=o_tasks)
    pd_res["max_max"] = [oIntra / 5, oInter / 5, np.mean(runTime)]

    oInter = 0
    oIntra = 0
    runTime = []
    for i in range(5):
        start = time.time()
        g = max_intra_min_inter(tasks=o_tasks, k=k, l=L)
        runTime.append(time.time() - start)
        oInter += inter(grouping=g, tasks=o_tasks)
        oIntra += intra(grouping=g, tasks=o_tasks)
    pd_res["max_min"] = [oIntra / 5, oInter / 5, np.mean(runTime)]

    output = pd.DataFrame.from_dict(pd_res, orient='index', columns=["intra_score", "inter_score", "running_time"])
    output.to_csv(f"./res/ours/our_alg_{n}_{k}.csv")

if __name__ == '__main__':
    simRunOurAlg()