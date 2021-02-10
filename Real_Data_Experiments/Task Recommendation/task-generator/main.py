import pandas as pd
from data_model import *
import sys, os
from algs import min_intra_min_inter, max_intra_max_inter, max_intra_min_inter, min_intra_max_inter
from scipy.spatial import distance
from mmr import mmr2
import click


with open('keywords.txt') as f :
    features = {'Answer.keyword{:02}'.format(i+1):k.strip() for i,k in enumerate(f.readlines())}

# features = []
# for i in TaskType.select():
#     features.extend(i.task_keywords)
# features = list(set(features))

# function for MMR algorithm
def sim_dim(tid_1, tid_2, dim):
    if 'creation' in dim:
        return (getattr(Task.get_by_id(tid_1).task_type, dim).timestamp() - getattr(Task.get_by_id(tid_2).task_type,
                                                                                    dim).timestamp()) ** 2
    return (getattr(Task.get_by_id(tid_1).task_type, dim) - getattr(Task.get_by_id(tid_2).task_type, dim)) ** 2


def sim_rel(worker_id, task_id, worker_keywords, task_type_features):
    if worker_id in worker_keywords.index:
        return 1 - distance.cosine(worker_keywords.loc[worker_id, :].values, task_type_features.loc[task_id, :].values)
    else:
        return 1


def write_to_file(dir_path, w, tasks, k, l):
    if k > len(tasks):
        raise IndexError("Not Enough Task provided.")
    with open("./data/assignments/{0}/{1}.tasks".format(dir_path, w), 'w') as f:
        f.write("#{0}".format(w))
        for i in range(k):
            f.write("\n")
            f.write("{")
            f.write(",".join(tasks[i]))
            f.write("}")


def select_good_tasks(w, worker_keywords, task_type_features, k, l, dim1, dim2):
    #
    # x = sorted({(t, TaskType.select().where(TaskType.task_type_id == t).get().requester): distance.cosine(
    #     worker_keywords.loc[w, :].values, task_type_features.loc[t, :].values) for t in range(1, 11)}.items(),
    #            key=lambda x: x[1])
    # x_good = [xx for xx in x if xx[1] < 0.4]
    # if len(x_good) < k:
    #     x_good = [xx for xx in x if xx[1] < 0.5]
    # if len(x_good) < k:
    #     x_good = [xx for xx in x if xx[1] < 0.6]
    # if len(x_good) < k:
    #     x_good = [xx for xx in x if xx[1] < 0.7]
    # if len(x_good) < k:
    #     x_good = [xx for xx in x if xx[1] < 0.9]
    # if len(x_good) < k:
    #     x_good = x[0:k]

    # x_tasks = [i[0][0] for i in x_good]
    if 'skill' in dim1:
        tasks = {str(t.id): (
            sum(worker_keywords.loc[w, task_type_features[t.task_type_id]].values), getattr(t.task_type, dim2)) for
            t in
            Task.select().order_by(fn.Random()).limit(k * l)}
    elif 'skill' in dim2:
        tasks = {str(t.id): (
            getattr(t.task_type, dim1),sum(worker_keywords.loc[w, task_type_features[t.task_type_id]].values)) for
            t in
            Task.select().order_by(fn.Random()).limit(k * l)}
    else:
        tasks = {str(t.id): (getattr(t.task_type, dim1), getattr(t.task_type, dim2)) for
                 t in
                 Task.select().order_by(fn.Random()).limit(k * l)}
    if 'creation' in dim2:
        for t in tasks:
            temp = (tasks[t][0], tasks[t][1].timestamp())
            tasks[t] = temp
    if 'creation' in dim1:
        for t in tasks:
            temp = (tasks[t][0].timestamp(),tasks[t][1])
            tasks[t] = temp
    return tasks


def clean_dims(dim1, dim2):
    DIM1 = dim1
    DIM2 = dim2
    if 'skill' in dim2:
        DIM1 = dim2
        DIM2 = dim1

    elif 'creation' in dim1:
        DIM2 = dim1
        DIM1 = dim2

    return DIM1, DIM2


@click.command()
@click.argument('worker_profiles_path', type=click.Path(exists=True))
@click.argument('num_sessions', default=3, type=click.INT)
@click.argument('session_length', default=3, type=click.INT)
@click.option('--alg', type=click.Choice(
    ['min_intra_max_inter', 'min_intra_min_inter', 'max_intra_max_inter', 'max_intra_min_inter']),
              default="min_intra_max_inter")
@click.option('--dim1', help="Which dimension of task to use",
              type=click.Choice(['skill','duration', 'creation_date', 'expected_pay']), default="skill")
@click.option('--dim2', help="Which dimension of task to use",
              type=click.Choice(['skill','duration', 'creation_date', 'expected_pay']), default="duration")
def main(worker_profiles_path, num_sessions, session_length, alg='min_intra_max_inter', dim1='duration',
         dim2='creation_date'):
    if not os.path.exists("./data") and not os.path.exists("./data/assignments"):
        os.mkdir("./data")
        os.chdir("./data")
        os.mkdir("./assignments")
        os.chdir("./assignments")
        os.mkdir("ours")
        os.mkdir("mmr")
        os.mkdir("random")
        os.chdir("..")
        os.chdir("..")

    workers = pd.read_csv(worker_profiles_path, encoding='latin')
    print("READ %s number of workers ..." % workers.shape[0])
    cols = ['WorkerId']
    cols.extend(list(features.keys()))
    worker_keywords = pd.DataFrame(0, columns=list(features.values()), index=workers.WorkerId)
    for i, wk in workers.loc[:,cols].iterrows():
        for feat in features:
            worker_keywords.loc[wk.WorkerId, features[feat]] = getattr(wk,feat)

    # for i, wk in workers.loc[:,cols].iterrows():
    #     for k in wk.Keywords.split('|'):
    #         if k in features:
    #             worker_keywords.loc[wk.WorkerId, k] = 1

    # GENERATING RANDOM SESSIONS
    print("GENERATING RANDOM SESSIONS...")
    for worker in worker_keywords.index:
        tasks = [str(t.id) for t in Task.select().order_by(fn.Random()).limit(num_sessions * session_length)]
        tasks = [tasks[i * session_length:(i + 1) * session_length] for i in range(num_sessions)]
        write_to_file('random', worker, tasks, num_sessions, session_length)

    print()
    print("*" * 20)
    print("GENERATING OUR ALGORITHM SESSIONS for :", alg, '...')
    task_type_features_2 = pd.DataFrame(0, columns=list(features.values()), index=range(1, 11))
    for t in TaskType.select():
        i = t.task_type_id
        for d in t.task_keywords:
            if d in task_type_features_2.columns:
                task_type_features_2.loc[i, d] = 1
    task_type_features = {i: [] for i in range(1, 11)}
    for t in TaskType.select():
        i = t.task_type_id
        for d in t.task_keywords:
            task_type_features[i].append(d)
    # GENERATING OUR ALGORITHM
    for w in sorted(worker_keywords.index):
        tasks = select_good_tasks(w, worker_keywords, task_type_features, num_sessions, session_length, dim1, dim2)
        if alg == 'min_intra_max_inter':
            grouping = min_intra_max_inter(tasks, num_sessions, session_length)
        elif alg == 'min_intra_min_inter':
            grouping = min_intra_min_inter(tasks, num_sessions, session_length)
        elif alg == 'max_intra_max_inter':
            grouping = max_intra_max_inter(tasks, num_sessions, session_length)
        else:
            grouping = max_intra_min_inter(tasks, num_sessions, session_length)

        write_to_file('ours', w, grouping, num_sessions, session_length)

    print()
    print("*" * 20)
    print("GENERATING MMR ALGORITHM SESSIONS for ...")
    for w in sorted(worker_keywords.index):
        # x = sorted({(t, TaskType.select().where(TaskType.task_type_id == t).get().requester): distance.cosine(
        #     worker_keywords.loc[w, :].values, task_type_features.loc[t, :].values) for t in range(1, 11)}.items(),
        #            key=lambda x: x[1])
        # x_good = [xx for xx in x if xx[1] < 0.4]
        # if len(x_good) < session_length:
        #     x_good = [xx for xx in x if xx[1] < 0.5]
        # if len(x_good) < session_length:
        #     x_good = [xx for xx in x if xx[1] < 0.6]
        # if len(x_good) < session_length:
        #     x_good = [xx for xx in x if xx[1] < 0.7]
        # if len(x_good) < session_length:
        #     x_good = [xx for xx in x if xx[1] < 0.9]
        # if len(x_good) < session_length:
        #     x_good = x[0:session_length]
        #
        # x_tasks = {i[0][0]: i[1] for i in x_good}
        # tasks = {str(t.id): x_tasks[t.task_type_id] for t in
        #          Task.select().where(Task.task_type.in_(list(x_tasks.keys()))).order_by(fn.Random()).limit(
        #              session_length * session_length * 2)}
        tasks = {str(t.id): task_type_features_2.loc[t.task_type_id].values for t in Task.select().order_by(fn.Random()).limit(session_length * num_sessions)}

        candidate, _ = mmr2(num_sessions * session_length, list(tasks.keys()), tasks,worker_keywords.loc[w].values, 0.1, 0.9)
        candidate = [candidate[i * session_length:(i + 1) * session_length] for i in range(num_sessions)]
        write_to_file('mmr', w, candidate, num_sessions, session_length)


if __name__ == '__main__':
    main()
