import itertools
import numpy as np
from scipy.spatial import distance
from ckmeans import ckmeans
from data_model import *
import random
from tsp import solve_tsp
import networkx as nx
import pprint
from copy import deepcopy
features = ['semantic similarity', 'sentence comparison', 'image annotation',
            'survey, academic, university research, quick',
            'content moderation', 'data categorization', 'data collection',
            'data validation', 'image categorization', 'search relevance',
            'semantic analysis', 'emotion detection', 'sentiment analysis',
            'transcription', 'data enrichment']


def intra(grouping):
    out = 0
    for g in grouping:
        g_m = np.mean([tasks[i][0] for i in g])
        out += sum([(tasks[i][0]-g_m)**2 for i in g])
    return out


def inter(grouping):
    out = []
    for g in grouping:
        out.append(np.mean([tasks[i][1] for i in g]))
    o = 0
    for i in range(len(out)-1):
        o += np.fabs(out[i] - out[i+1])
    return o


def best_inter(grouping):
    best_inter = 0
    best_g = None
    for x in itertools.permutations(grouping.keys()):
        g = {i:grouping[x[i]] for i in range(len(grouping))}
        score = inter(g)
        if score > best_inter:
            best_inter = score
            best_g = g
    return best_g,best_inter


def estiamte_min_intra(data,n_s,k,l):
    itr = 0
    best_g = {}
    best_score = 0
    while itr < n_s :
        temp = random.sample(data,k*l)
        g = {i:temp[i*l:(i+1)*l] for i in range(k)}
        score = intra(g)
        if itr == 0 or score < best_score :
            best_g = g
            best_score = score
        itr += 1
    best_g = {i:sorted(sorted(best_g.values(),key=lambda x:np.mean(x))[i],key=lambda x:x.d1) for i in range(k)}
    return best_g,best_score

def print_g(grouping, *args):
    for g in grouping:
        print(g, grouping[g], '-->', np.mean(grouping[g]))
    print(*args)


def create_bins(T,k,l,mu_g):

    left_bin,mid_bin,right_bin = [],[],[]
    pos_map = sorted([(i,np.fabs(x[1]-mu_g)) for i,x in enumerate(T)],key=lambda x:x[1])
    mid = [pos_map[i][0] for i in range(k)]
    _tasks = [T[i] for i in range(len(T)) if i not in mid]
    for i in mid:
        mid_bin.append(T[i])

    mid_bin = sorted(mid_bin,key=lambda x:x[1])

    for x in _tasks:
        if x[1] < mu_g:
            left_bin.append(x)
        else:
            right_bin.append(x)
    while len(left_bin) < len(right_bin):
        temp_mid = mid_bin.pop(0)
        temp = right_bin.pop(0)
        left_bin.append(temp_mid)
        mid_bin.append(temp)
    while len(left_bin) > len(right_bin):
        temp_mid = mid_bin.pop()
        temp = left_bin.pop()
        right_bin.insert(0,temp_mid)
        mid_bin.insert(0,temp)
    bins = []
    left_overs = []
    for i in range(0,int((l-1)/2)):
        bins.append(left_bin[i*k:(i+1)*k])
    if len(left_bin) > (i+1)*k:
        left_overs.extend(left_bin[(i+1)*k:])
    if len(left_overs) > 0 :
        while len(left_overs) < k:
            left_overs.append(mid_bin.pop(0))
        bins.append(left_overs)
    while len(mid_bin)<k:
        mid_bin.append(right_bin.pop(0))
    bins.append(mid_bin)
    for i in range(0,int((l-1)/2)):
        bins.append(right_bin[i*k:(i+1)*k])

    return bins

def max_intra_cluster(tasks,k,l):
    _tasks = sorted(tasks,key=lambda x: x[1])
    mu_g = sum([x[1] for x in tasks]) / len(tasks)
    bins = create_bins(_tasks,k,l,mu_g)
    for i,b in enumerate(bins):
        mu_b = sum([x[1] for x in b]) / len(b)
        if mu_g < mu_b:
            bins[i] = sorted(b,key=lambda x:x[1],reverse=True)
    ans = []
    for i in range(k):
        g = []
        for j in range(l):
            g.append(bins[j][i])
        ans.append(g)
    return ans



def min_inter_cluster(tasks,k,l):
    groupings = max_intra_cluster(tasks,k,l)

    distance_matrix = np.zeros((k,k))
    for i in range(k):
        for j in range(i+1,k):
            if i == j:
                distance_matrix[i, j] = 0
            else:
                avg_i = sum([x[1] for x in groupings[i]])/l
                avg_j = sum([x[1] for x in groupings[j]]) / l
                distance_matrix[i,j] = (avg_i - avg_j)**2
                distance_matrix[j,i] = distance_matrix[i,j]
    ordering = solve_tsp(distance_matrix)
    out = [groupings[i] for i in ordering]
    return out


def max_intra_min_inter(tasks,k,l):
    """
    :param tasks: Gets a dict of tasks ids and tuples. The first element of the tuple is the first dimension of taks
    the second element is the second dimension of the task
    :param k: Number of groups
    :param l: Number of tasks in a single session
    :return:
    """
    dim1 = [(i,tasks[i][0]) for i in tasks]
    dim2 = {i:tasks[i][1] for i in tasks}
    groupings = max_intra_cluster(dim1, k, l)
    distance_matrix = np.zeros((k,k))
    for i in range(k):
        for j in range(i+1,k):
            if i == j:
                distance_matrix[i, j] = 0
            else:
                avg_i = sum([dim2[x[0]] for x in groupings[i]])/l
                avg_j = sum([dim2[x[0]] for x in groupings[j]]) / l
                distance_matrix[i,j] = (avg_i - avg_j)**2
                distance_matrix[j,i] = distance_matrix[i,j]
    ordering = solve_tsp(distance_matrix)
    out = []
    for i in ordering:
        temp = []
        for j in groupings[i]:
            temp.append(j[0])
        out.append(temp)

    return out


def max_intra_max_inter(tasks,k,l):
    """
    :param tasks: Gets a dict of tasks ids and tuples. The first element of the tuple is the first dimension of taks
    the second element is the second dimension of the task
    :param k: Number of groups
    :param l: Number of tasks in a single session
    :return:
    """
    dim1 = [(i,tasks[i][0]) for i in tasks]
    dim2 = {i:tasks[i][1] for i in tasks}
    groupings = max_intra_cluster(dim1, k, l)
    distance_matrix = np.zeros((k,k))
    for i in range(k):
        for j in range(i+1,k):
            if i == j:
                distance_matrix[i, j] = 0
            else:
                avg_i = sum([dim2[x[0]] for x in groupings[i]])/l
                avg_j = sum([dim2[x[0]] for x in groupings[j]]) / l
                distance_matrix[i,j] = -(avg_i - avg_j)**2
                distance_matrix[j,i] = distance_matrix[i,j]
    ordering = solve_tsp(distance_matrix)
    out = []
    for i in ordering:
        temp = []
        for j in groupings[i]:
            temp.append(j[0])
        out.append(temp)
    return out


def min_intra_min_inter(tasks,k,l):
    dim1 = [(i,tasks[i][0]) for i in tasks]
    dim2 = {i:tasks[i][1] for i in tasks}
    clusters = ckmeans(dim1,k,l)
    for g in range(k):
        while len(clusters[g]) < l:
            clusters[g].append((None,clusters[g][0][1]))
        while len(clusters[g]) >l :
            clusters[g].pop(-1)
    distance_matrix = np.zeros((k,k))
    for i in range(k):
        for j in range(i+1,k):
            if i == j:
                distance_matrix[i, j] = 0
            else:
                avg_i = sum([dim2[x[0]] for x in clusters[i]])/l
                avg_j = sum([dim2[x[0]] for x in clusters[j]]) / l
                distance_matrix[i,j] = (avg_i - avg_j)**2
                distance_matrix[j,i] = distance_matrix[i,j]
    ordering = solve_tsp(distance_matrix)
    out = []
    for i in ordering:
        temp = []
        for j in clusters[i]:
            temp.append(j[0])
        out.append(temp)

    return out



def min_intra_max_inter(tasks,k,l):
    dim1 = [(i,tasks[i][0]) for i in tasks]
    dim2 = {i:tasks[i][1] for i in tasks}
    clusters = ckmeans(dim1,k,l)
    for g in range(k):
        while len(clusters[g]) < l:
            clusters[g].append((None,clusters[g][0][1]))
        while len(clusters[g]) >l :
            clusters[g].pop(-1)

    distance_matrix = np.zeros((k,k))
    for i in range(k):
        for j in range(i+1,k):
            if i == j:
                distance_matrix[i, j] = 0
            else:
                avg_i = sum([dim2[x[0]] for x in clusters[i]])/l
                avg_j = sum([dim2[x[0]] for x in clusters[j]]) / l
                distance_matrix[i,j] = -(avg_i - avg_j)**2
                distance_matrix[j,i] = distance_matrix[i,j]
    ordering = solve_tsp(distance_matrix)
    out = []
    for i in ordering:
        temp = []
        for j in clusters[i]:
            temp.append(j[0])
        out.append(temp)
    return out


if __name__ == '__main__':
    N = 8192
    K = 1024
    L = N // K
    tasks = {i:(np.random.randint(0,500),np.random.randint(0,500)) for i in range(N)}
    o = max_intra_min_inter(tasks,K,L)
    o2 = max_intra_max_inter(tasks,K ,L)
    r = []
    keys = list(tasks.keys())
    for i in range(K):
        temp = keys[i*L:(i+1)*L]
        r.append(temp)
    print('o : intra : ',intra(o),'inter : ',inter(o))
    print('o2 : intra : ', intra(o2), 'inter : ', inter(o2))
    print('r : intra : ', intra(r), 'inter : ', inter(r))
    # for g in o:
    #     mu_g = sum([x[1] for x in g])/len(g)
    #     print(g,mu_g)

#     task_type_features = pd.DataFrame(0,columns=features,index=range(1,11))
#     for t in TaskType.select():
#         i = t.task_type_id
#         for d in t.task_keywords:
#             task_type_features.loc[i,d] = 1
#
#     workers = pd.read_csv('data/worker_profiles.csv', encoding='latin')
#     worker_keywords = pd.DataFrame(0, columns=features, index=workers.WorkerId)
#     for i, wk in workers.loc[:, ['Keywords', 'WorkerId']].iterrows():
#         for k in wk.Keywords.split('|'):
#             worker_keywords.loc[wk.WorkerId, k] = 1
#
#
# def cc(T,i,j):
#     x = sum(t ** 2 for t in T[i - 1:j])
#     return x - ((j - i + 1) * np.mean(T[i - 1:j]) ** 2)
#
#
# def min_intra(T,k,l):
#     N = len(T)
#     T = sorted(T)
#     D = np.zeros(k+1,N+1)
#
#     for m in range(1,N+1):
#         D[1,m] = cc(T,1,m)



