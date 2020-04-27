# ______________________________________________________________________________
# Genetic Algorithm


import sys
from collections import deque
from collections import OrderedDict 
import numpy
from itertools import islice, chain

from utils import *

def genetic_search(problem, ngen=1000, pmut=0.1, n=20):
    """Call genetic_algorithm on the appropriate parts of a problem.
    This requires the problem to have states that can mate and mutate,
    plus a value method that scores states."""

    # NOTE: This is not tested and might not work.
    # TODO: Use this function to make Problems work with genetic_algorithm.

    s = problem.initial_state
    states = [problem.result(s, a) for a in problem.actions(s)]
    random.shuffle(states)
    return genetic_algorithm(states[:n], problem.value, ngen, pmut)


def genetic_algorithm(population, fitness_fn, domains,
 f_thres=None, ngen=1000, pmut=0.1):
    """[Figure 4.8]"""
    stats = []
    for i in range(ngen):
        fitnesses = list(map(fitness_fn, population))
        maxfit=max(fitnesses)
        stats.append({'generation':i,'mean':mean(fitnesses),'max':maxfit,'min':min(fitnesses)})
        print('Fitness Stats '+str(stats[-1]))
        
        if f_thres != None and maxfit >= f_thres:
            return population[fitnesses.index(maxfit)], stats
        
        population = [mutate(recombine(*select(2, population, fitnesses)), domains, pmut)
                      for i in range(len(population))]

    #Log final generation's stats
    fitness = list(map(fitness_fn, population))
    maxfitness=max(fitness)
    stats.append({'generation':i+1,'mean':mean(fitness),'max':max(fitness),'min':min(fitness)})
    print('Fitness Stats '+str(stats[-1]))
    
    return population[fitness.index(maxfitness)], stats


def init_population(pop_number, variables, domains):
    """Initializes population for genetic algorithm
    pop_number  :  Number of individuals in population
    gene_pool   :  List of possible values for individuals
    """
    population = []
    for i in range(pop_number):
        new_individual = {}
        for v in variables:
            # randomly choose an assignment from this variable's domain
            ind = np.random.choice(len(domains[v]))
            new_individual[v] = domains[v][ind]
        population.append(OrderedDict(sorted(new_individual.items())) )

    return population


def select(r, population, fitnesses):
    
    #We need to normalize the fitness scores for the weighted_sampler function.
    minFitness = min(fitnesses)
    zeroAdjusted = list(map(lambda x : x + abs(minFitness), fitnesses))
    normalizationFactor = numpy.linalg.norm(zeroAdjusted)
    if normalizationFactor == 0:
        normalFitnesses = zeroAdjusted
    else:
        normalFitnesses = zeroAdjusted/normalizationFactor
    
    sampler = weighted_sampler(population, normalFitnesses)
    return [sampler() for i in range(r)]


def recombine(x, y):
    n = len(x)
    c = random.randrange(0, n)
    return OrderedDict(
        chain(
            islice(x.items(), c),
            islice(y.items(), c, len(y))))


def recombine_uniform(x, y):
    n = len(x)
    result = [0] * n
    indexes = random.sample(range(n), n)
    for i in range(n):
        ix = indexes[i]
        result[ix] = x[ix] if i < n / 2 else y[ix]

    return ''.join(str(r) for r in result)

def mutate(class_set, domains, pmut):
    if random.uniform(0, 1) >= pmut:
        return class_set
    
    class_index = random.randint(0, len(class_set)-1)
    old_gene = list(class_set.items())[class_index]
    class_name = old_gene[0]
    new_gene = {class_name:random.choice(domains[class_name])}
    
    #print('Original: '+str(old_gene))
    #print('Mutated: '+str(new_gene))
    
    return OrderedDict(
        chain(
            islice(class_set.items(), class_index),
            new_gene.items(),
            islice(class_set.items(), class_index + 1, len(class_set))))