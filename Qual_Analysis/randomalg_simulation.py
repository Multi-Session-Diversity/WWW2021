import random
import click
import pickle
import time
import numpy as np


# Modified this for the songs experiment
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


def getTasks(fileName, numberOfTasks):
    """fileName: Name of file containing the tasks"""
    """numberOFTasks: How many tasks you need"""
    tasks = pickle.load(open(fileName, 'rb'))
    taskOutput = {}
    for i in range(numberOfTasks):
        taskOutput[i + 1] = tasks[i]
    return taskOutput


"""
Function takes 3 parameters:
1. k : Number of clusters
2. l: Number of tasks per session
3. task_dict: A dictionary consisting of tasks. Dictionary keys represent task index and value are tuples
              containing more information about the task

Returns a list of k lists consisting of l unique task indexes. 
Constraint due to non fuzzy approach is k*l must equal total number of tasks 
"""


def randomize_non_fuzzy(k, l, task_dict):
    n = k * l  # Number of tasks
    if (k * l != len(task_dict)):
        statement = "Invalid k and l value. K*l must equal number of tasks"
        return statement
    numOfTasks = len(task_dict)
    listOfTaskIndex = [taskIdx for taskIdx in task_dict]
    output = []
    while len(listOfTaskIndex) > 0:
        toAdd = random.sample(listOfTaskIndex, l)
        output.append(toAdd)
        for idx in toAdd:
            listOfTaskIndex.remove(idx)

    return output


"""
Function takes 3 parameters:
1. k : Number of clusters
2. l: Number of tasks per session
3. task_dict: A dictionary consisting of tasks. Dictionary keys represent task index and value are tuples
              containing more information about the task

Returns a list of k lists consisting of l  task indexes(Not necessirly unique due to fuzzy clustering). 
"""


def randomize_fuzzy(k, l, task_dict):
    numOfTasks = len(task_dict)
    listOfTaskIndex = [taskIdx for taskIdx in task_dict]
    output = []
    while len(output) < k:
        toAdd = list(np.random.choice(listOfTaskIndex, l))
        output.append(toAdd)

    return output


@click.command()
@click.option('--dist', prompt='Which distribution',
              type=click.Choice(['d3_tempo_loudness',
                                 'd2_release_artist_familiarity',
                                 'd1_duration_hotness']))  
# @click.option('--n',prompt='Number of Tasks(N)',type=click.INT)
@click.option('--choice', prompt='Which thing to hold constant', type=click.Choice(['n', 'k']))
# @click.option('--k',prompt='Number Of sessions(K)',type=click.INT)

def runSim(choice, dist):
    if (str(choice) == 'k'):  # Run all N values with K constant
        k = 128
        nValues = [1024, 2048, 4096, 8192, 16384, 32768, 65536]
        for n in nValues:
            l = n // k
            start = time.time()
            oInter = 0
            oIntra = 0
            tasks = getTasks("./data/"+str(dist) + '.p', k * l)
            for i in range(5):
                r = randomize_non_fuzzy(k, l, tasks)
                oInter += inter(r, tasks)
                oIntra += intra(r, tasks)
            end = time.time()
            runTime = end - start
            message = 'randomAlg, N =' + str(k * l) + ', K= ' + str(k) + " Intra: " + str(
                oIntra / 5) + " Inter: " + str(oInter / 5) + " Runtime = " + str(runTime)
            writeResults('./res/random/data_randomAlg_kConst.txt', message)
        return

    elif (str(choice) == 'n'):  # Run all k values with N constant
        n = 8192
        kValues = [16, 32, 64, 128, 256, 512, 1024, 2048]
        for k in kValues:
            l = n // k
            start = time.time()
            oInter = 0
            oIntra = 0
            tasks = getTasks("./data/"+str(dist) + '.p', k * l)
            for i in range(5):
                r = randomize_non_fuzzy(k, l, tasks)
                oInter += inter(r, tasks)
                oIntra += intra(r, tasks)
            end = time.time()
            runTime = end - start
            message = 'randomAlg, N =' + str(k * l) + ', K= ' + str(k) + " Intra: " + str(
                oIntra / 5) + " Inter: " + str(oInter / 5) + " Runtime = " + str(runTime)
            writeResults('./res/random/data_randomAlg_nConst.txt', message)
        return
    else:
        print("Something went wrong !")
        return


if __name__ == '__main__':
    runSim()
