
import numpy as np
import random

class Cluster:
    def __init__(self,kernel,elements=None):
        self.kernel = kernel
        self.elements = [] if elements is None else elements

    def __repr__(self):
        return 'Center | {0}'.format(self.kernel)





def CT(X, alpha, beta, delta, gamma, num_itr, worker, k, L, sim, div, m):
    S_w = []
    alpha_prime = alpha + beta + delta + gamma
    beta_prime = delta_prime = gamma_prime = 0

    C = [Cluster(kernel=kernel) for kernel in random.sample(X,k)]
    W = {}
    for x in X:
        for c in C:
            W[(x,c)] = 0
    itr = 0
    while itr < num_itr :
        alpha_prime = alpha_prime - (beta + gamma + delta) / num_itr
        beta_prime += beta/num_itr
        delta_prime = + delta / num_itr
        gamma_prime += gamma/num_itr
        while True:
            for x_i in X:
                for c_j in C:
                    W[(x_i,c_j)] = 1/sum([(sim(x_i,c_j)/sim(x_i,c_k))**(1/(m-1)) for c_k in C])

            for c in C:
                while len(c.elements) < L:
                    candids = {}
                    X_P = set(X) - set(c.elements)
                    for x in X_P:
                        beta_sim_x_cj = beta_prime*sim(x,c)
                        sum_div = (delta_prime/len(c.elements)) * sum(div(x,y) for y in c.elements)
                        sim_w_x = gamma_prime * sim(worker,x)
                        score = beta_sim_x_cj+sum_div+sim_w_x
                        candids[x] = score
                    candid = max(candids,key=lambda x: x[1])
                    c.elements.append(candid)

            for c_j in C:
                sum_w_ij = sum(((W[x,c_j])**m)*X[x] for x in X)
                sum_members = (beta_prime)
                c_j.kernel = (alpha/len(X))
        itr +=1


