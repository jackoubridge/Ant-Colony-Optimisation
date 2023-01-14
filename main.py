import numpy as np
import random
import csv
import sys

def read_data(file): 
    """
    Returns data read from a file.

        Parameters:
            file (string): The name of the file to be read

        Returns:
            [n, d, f] (list): 2D list of specific sections of the file
    """
    
    with open(file, 'r') as f:
        data = []
        for line in f:
            data.append([int(x) for x in line.split() if x])

    n = int(data[0][0])
    d = data[2:52][:n]
    f = data[53:103][:n]
    return [n, d, f]


def generate_path(n, start, pheromones):
    """
    Calculates the path of an ant.

        Parameters:
            n (int): Number of locations/facilities in the graph
            start (int): The index value of the first node in the path
            pheromones (numpy array): Values of the pheromones on each link in the graph

        Returns:
            path (list): Computed path of the ant
    """

    path = np.array([start]) # Set the path equal to only the start node
    all_nodes = np.arange(0, n) # Initialise list of all nodes in the graph

    for i in range(1, n):
        next_nodes = np.delete(all_nodes, path) # Remove visited nodes from next available nodes
        if i == (n-1):
            choice = next_nodes[0] # If only one choice remains, choose it
        else:
            next_pheromones = np.delete(pheromones[path[-1]], path) # Get pheromones for all potential next nodes
            choice = random.choices(next_nodes, weights=next_pheromones, cum_weights=None, k=1) # Random weighted choice based on pheromones
        path = np.append(path, choice) # Append choice to path
    return path


def get_fitness(path, d, f):
    """
    Caclulates the fitness of a given ant path.

        Parameters:
            path (string): The path of an ant
            d (numpy array): Matrix of distances between locations
            f (numpy array): Matrix of flow between facilities

        Returns:
            fitness (int): The calculated fitness of the path
    """

    fitness = 0
    for i in range(len(path)):
        for j in range(len(path)):
            fitness += d[i][j] * f[path[i]][path[j]] # Loop through all nodes and sum f * d
    return fitness


def update_pheromones(oneover, path, n):
    """
    Calculates the amount which pheromones should change on graph links.

        Parameters:
            oneover (numpy longdouble): 1/fitness for a path
            path (list): The path of an ant
            n (int): The number of locations/facilities in the graph

        Returns:
            p (numpy array): Matrix of the amount that certain pheromones should change
    """
    p = np.zeros((n,n),dtype='longdouble')
    for x in range(len(path) -1):
        p[path[x]][path[x+1]] += np.longdouble(oneover) # Add 1/fitness to correct links
    return p


def main(m, e):
    best_fitness = float('inf') # Initialise best fitness to infinity so it will be overriden by the next best
    data = read_data('Uni50a.dat')

    # Read data
    n = data[0]
    d = np.array(data[1])
    f = np.array(data[2])

    pheromones = np.random.rand(n, n) # Initialise random pheromones

    iterations = int(10000/m) # Fitness evaluations / number of ants = number of iterations

    start = np.random.randint(0, n) # Inistalise random start node

    average_fitness_list = [] # Initialise list to store the average fitness per iteration

    for x in range(iterations):
        total_fitness = 0
        pheromone_update = np.zeros((n, n), dtype='longdouble')

        for y in range(m): # For each and in an iteration
            path = generate_path(n, start, pheromones) # Generate the ant's path
            fitness = get_fitness(path, d, f) # Calculate the path's fitness
            if fitness < best_fitness: # Check if it is the best fitness, replace if so
                    best_fitness = fitness
            total_fitness += fitness
            oneover = np.longdouble(np.longdouble(1)/np.longdouble(fitness)) # Calculate 1/fitness, this is added to pheromone links
            pheromone_update = np.add(pheromone_update, update_pheromones(oneover, path, n))
        
        pheromones = np.add(pheromones, pheromone_update)
        pheromones *= e # Evaporate all pheromone links
        
        average_fitness_list.append(total_fitness / m)
    return(average_fitness_list, best_fitness)

def experiments(filename, m, e): # Write experiments to csv file
    biglist = []
    bestlist = []
    for x in range(5):
            result = main(m, e)
            bestlist.append(result[1])
            biglist.append(result[0])

    numlist = np.arange(len(biglist[0]))

    with open(filename, 'a') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(numlist)
        for i in biglist:
            writer.writerow(i)

    print("m: %s, e: %s\nBest: %s" % (m, e, bestlist), flush = True) # Print results
    print(np.mean(bestlist))

if __name__ == '__main__':

    FILENAME = "output.csv" # Default file to output results
    M = 100 # Number of ants
    E = 0.5 # Pheromone evaporation rate

    # Check for command-line arguments as parameters
    if len(sys.argv) > 1:
        experiments(sys.argv[1], int(sys.argv[2]), float(sys.argv[3]))
    else:
        experiments(FILENAME, M, E) # Otherwise run with default parameters

