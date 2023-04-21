import random

# Tamaño de la matriz
tamano_matriz = 3

# Número máximo de iteraciones
maximo_iteraciones = 1000

# Tamaño de la población
tamano_poblacion = 100

# Probabilidad de mutación
probabilidad_de_mutacion = 0.1

# Función de aptitud
def funcion_fitness(solucion):
    # Penalizaciones por repetición y por números consecutivos
    repeat_penalty = len(solucion) - len(set(solucion))
    consecutive_penalty = 0
    for i in range(tamano_matriz):
        for j in range(tamano_matriz):
            index = i * tamano_matriz + j
            if index > 0 and abs(solucion[index] - solucion[index - 1]) == 1:
                consecutive_penalty += 1
            if index >= tamano_matriz and abs(solucion[index] - solucion[index - tamano_matriz]) == 1:
                consecutive_penalty += 1
    return 1.0 / (1.0 + repeat_penalty + consecutive_penalty)

# Generación de la población inicial
poblacion = []
for i in range(tamano_poblacion):
    solucion = random.sample(range(1, tamano_matriz ** 2 + 1), tamano_matriz ** 2)
    poblacion.append(solucion)

# Bucle principal
for iteration in range(maximo_iteraciones):
    # Evaluación de la población
    fitness = []
    for solucion in poblacion:
        fitness.append(funcion_fitness(solucion))

    # Selección de padres
    parents = []
    for i in range(tamano_poblacion):
        index1 = random.randint(0, tamano_poblacion - 1)
        index2 = random.randint(0, tamano_poblacion - 1)
        if fitness[index1] > fitness[index2]:
            parents.append(poblacion[index1])
        else:
            parents.append(poblacion[index2])

    # Cruzamiento y mutación
    offspring = []
    for i in range(tamano_poblacion):
        parent1 = parents[random.randint(0, tamano_poblacion - 1)]
        parent2 = parents[random.randint(0, tamano_poblacion - 1)]
        crossover_point1 = random.randint(0, tamano_matriz ** 2 - 1)
        crossover_point2 = random.randint(crossover_point1, tamano_matriz ** 2 - 1)
        child = parent1[:crossover_point1] + parent2[crossover_point1:crossover_point2] + parent1[crossover_point2:]
        if random.random() < probabilidad_de_mutacion:
            mutation_point = random.randint(0, tamano_matriz ** 2 - 1)
            mutation_value = random.randint(1, tamano_matriz ** 2)
            child[mutation_point] = mutation_value
        offspring.append(child)

    # Selección de supervivientes
    combined_population = poblacion + offspring
    combined_fitness = []
    for solucion in combined_population:
        combined_fitness.append(funcion_fitness(solucion))
    combined_index = list(range(len(combined_population)))
    combined_index.sort(key=lambda x: combined_fitness[x], reverse=True)
    poblacion = [combined_population[i] for i in combined_index[:tamano_poblacion]]

# Devolución de la mejor solución encontrada
mejor_fitness = 0
mejor_solucion = None
for solucion in poblacion:
    fitness = funcion_fitness(solucion)
    if fitness > mejor_fitness:
        mejor_fitness = fitness
        mejor_solucion = solucion

print("Mejor solución encontrada: ",mejor_solucion)