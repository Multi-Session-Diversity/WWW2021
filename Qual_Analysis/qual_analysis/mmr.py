

import numpy as np
from scipy.spatial import distance
import itertools
import time

def dist_func(d1,d2):
    return (d1-d2)**2


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


# NEW MMR ALGORITHM
def mmr_new(tasks:dict,k,l,_l1,_l2,func1,func2):
    """
    This is the new MMR algorithm,
    :param tasks: a Dictionary of tasks to be used
    :param k: the number of windows
    :param l: the length of each window
    :param _l1: a weight for the Intra part
    :param _l2: a weight for the Inter part
    :param func1: the Max or Min of Intra part
    :param func2: the Max or Min of Inter part
    :return: a list of 'k' list of each with the length 'l' containing indices of 'tasks'
    """
    dim1 = {i:tasks[i][0] for i in tasks}
    dim2 = {i: tasks[i][1] for i in tasks}
    dist_matrix_dim1 = {}
    # for i in tasks:
    #     for j in tasks:
    #         if i == j:
    #             continue
    #         dist_matrix_dim1[(i,j)] = (dim1[i]-dim1[j])**2
    groups = [list() for _ in range(k)]
    available = list(tasks.keys())
#     randomly assign some tasks to the empty lists
    selected = np.random.choice(available,k,False)
    for i in range(k):
        groups[i].append(selected[i])
        available.remove(selected[i])
    itr = 0
    tasks_must_select = k
    while tasks_must_select < k * l:
        groups_mean = [np.mean([dim2[i] for i in g]) for g in groups]
        if len(groups[itr]) < l:
            mmr_score = [(x,_l1 * sum([dist_func(dim1[x],dim1[y]) for y in groups[itr]]) +
                          _l2 * func2([np.fabs(groups_mean[i] - (groups_mean[itr] * len(groups[itr]) + dim2[x]) / (len(groups[itr]) + 1)) for i in range(k) if i != itr])) for x in available]
            candidate = func1(mmr_score,key = lambda x:x[1])

            groups[itr].append(candidate[0])
            available.remove(candidate[0])
            tasks_must_select += 1
        itr += 1
        if itr == k:
            itr = 0

    return groups

# FASTER MMR
def mmr_new_fast(tasks:dict,k,l,_l1,_l2,func1,func2):
    """
    This is the new MMR algorithm,
    :param tasks: a Dictionary of tasks to be used
    :param k: the number of windows
    :param l: the length of each window
    :param _l1: a weight for the Intra part
    :param _l2: a weight for the Inter part
    :param func1: the Max or Min of Intra part
    :param func2: the Max or Min of Inter part
    :return: a list of 'k' list of each with the length 'l' containing indices of 'tasks'
    """
    dim1 = {i:tasks[i][0] for i in tasks}
    dim2 = {i: tasks[i][1] for i in tasks}
    dist_matrix_dim1 = {}
    # for i in tasks:
    #     for j in tasks:
    #         if i == j:
    #             continue
    #         dist_matrix_dim1[(i,j)] = (dim1[i]-dim1[j])**2
    groups = [list() for _ in range(k)]
    available = list(tasks.keys())
#     randomly assign some tasks to the empty lists
    selected = np.random.choice(available,k,False)
    for i in range(k):
        groups[i].append(selected[i])
        available.remove(selected[i])
    itr = 0
    tasks_must_select = k
    while tasks_must_select < k * l:
        groups_mean = [np.mean([dim2[i] for i in g]) for g in groups]
        if len(groups[itr]) < l:
            mmr_score = [(x,_l1 * sum([dist_func(dim1[x],dim1[y]) for y in groups[itr]]) +
                          _l2 * func2([np.fabs(groups_mean[i] - (groups_mean[itr] * len(groups[itr]) + dim2[x]) / (len(groups[itr]) + 1)) for i in range(k) if i != itr])) for x in available]
            scores = sorted(mmr_score,key = lambda x:x[1])
            if func1 == max:
                candidates = scores[-1:-(l):-1]
            elif func1 == min:
                candidates = scores[0:l-1]
            else:
                raise NotImplementedError()
            groups[itr].extend([c[0] for c in candidates])
            for c in candidates:
                available.remove(c[0])
                tasks_must_select += 1
        itr += 1
        if itr == k:
            itr = 0

    return groups


if __name__ == '__main__':
    N = 600
    K = 60
    L = 10
    tasks = {i:(np.random.randint(0,500),np.random.randint(0,500)) for i in range(N)}
    worker = (np.random.randint(0,500),np.random.randint(0,500))
    start=time.time()
    c = mmr_new_fast(tasks,K,L,0.2,0.8,max,max)
    end=time.time()
    #print(end-start)
    #print(intra(c, tasks))

