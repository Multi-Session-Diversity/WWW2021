

import numpy as np
from scipy.spatial import distance
import itertools


def cosine_sim(x,y):
    return 1 - distance.cosine(x,y)

def intra(grouping,tasks):
    out = 0
    for g in grouping:
        g_m = np.mean([tasks[i][0] for i in g])
        out += sum([(tasks[i][0]-g_m)**2 for i in g])
    return out


def inter(grouping,tasks):
    out = []
    for g in grouping:
        out.append(np.mean([tasks[i][1] for i in g]))
    o = 0
    for i in range(len(out)-1):
        o += np.fabs(out[i] - out[i+1])
    return o


def mmr(num_tasks,tasks,worker, _lambda,_lambda2, sim1_func,sim2_func,dim,worker_keys,task_keys):
    selected = []
    scores = []
    itr = 0
    while itr < num_tasks and itr < len(tasks):
        remainder = set(tasks) - set(selected)
        mmr_scores = [(x,_lambda*sim1_func(x,worker,worker_keys,task_keys) - (_lambda2)*max([sim2_func(x,y,dim) for y in set(selected)-{x}] or [0])) for x in remainder]
        candidate = max(mmr_scores,key=lambda x : x[1])
        selected.append(candidate[0])
        scores.append(candidate)
        itr +=1
    return selected,scores


def mmr2(num_tasks,tasks,tasks_vec,worker, _lambda,_lambda2):
    selected = []
    scores = []
    itr = 0
    while itr < num_tasks and itr < len(tasks):
        remainder = set(tasks) - set(selected)
        mmr_scores = [(x, _lambda*cosine_sim(worker,tasks_vec[x]) - (_lambda2)*max([cosine_sim(tasks_vec[x],tasks_vec[y])for y in set(selected)-{x}] or [0])) for x in remainder]
        candidate = max(mmr_scores,key=lambda x : x[1])
        selected.append(candidate[0])
        scores.append(candidate)
        itr += 1
    return selected,scores


def mmr_sim(num_tasks,tasks,worker, _lambda,_lambda2, sim1_func,sim2_func):
    selected = []
    scores = []
    itr = 0
    while itr < num_tasks and itr < len(tasks):
        # print(itr)
        remainder = set(tasks) - set(selected)
        mmr_scores = [(x,_lambda*sim1_func(tasks[x],worker) - (_lambda2)*max([sim2_func(tasks[x],tasks[y]) for y in set(selected)-{x}] or [0])) for x in remainder]
        candidate = max(mmr_scores,key=lambda x : x[1])
        selected.append(candidate[0])
        scores.append(candidate)
        itr +=1
    return selected,scores


def lunch_mmr(tasks:dict,worker,k,l,_lambda1,_lambda2):
    assert len(tasks[list(tasks.keys())[0]]) == len(worker)  # Check if the number of keywords for tasks is the same as worker
    candidate,_ = mmr_sim(k*l,tasks,worker,_lambda1,_lambda2,cosine_sim,cosine_sim)

    candidate = [candidate[i * l:(i + 1) * l] for i in range(k)]
    return candidate     # WARNING : THIS IS A LIST OF INDICES !!!


if __name__ == '__main__':
    N = 128
    K = 4
    L = N // K
    tasks = {i:(np.random.randint(0,500),np.random.randint(0,500)) for i in range(N)}
    worker = (np.random.randint(0,500),np.random.randint(0,500))
    c = lunch_mmr(tasks,worker,K,L,0.2,0.8)
