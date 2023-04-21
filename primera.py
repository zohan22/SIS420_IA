import heapq
from collections import deque
import random

class ColaPrioridadLimitada(object):
    def __init__(self, limite=None, *args):
        self.limite = limite
        self.queue = list()

    def __getitem__(self, val):
        return self.queue[val]

    def __len__(self):
        return len(self.queue)

    def push(self, x):
        heapq.heappush(self.queue, x)
        if self.limite and len(self.queue) > self.limite:
            self.queue.remove(heapq.nlargest(1, self.queue)[0])

    def pop(self):
        return heapq.heappop(self.queue)

    def extend(self, iterable):
        for x in iterable:
            self.append(x)

    def clear(self):
        for x in self:
            self.queue.remove(x)

    def remove(self, x):
        self.queue.remove(x)

    # Metodo para saber si la cola esta vacia
    def empty(self):
        if not self.heap:
            return True
        else:
            return False
        
    def sorted(self):
        return heapq.nsmallest(len(self.queue), self.queue)
    
class NodoBusqueda(object):
    '''Nodo para el proceso de busqueda.'''

    def __init__(self, estado, padre=None, accion=None, costo=0, problema=None, profundidad=0):
        self.estado = estado
        self.padre = padre
        self.accion = accion
        self.costo = costo
        self.problema = problema or padre.problema
        self.profundidad = profundidad

    def expandir(self, busqueda_local=False):
        '''Crear sucesores.'''
        nodos_nuevos = []
        for accion in self.problema.acciones(self.estado):
            estado_nuevo = self.problema.resultado(self.estado, accion)
            costo = self.problema.costo(self.estado, accion, estado_nuevo)
            fabrica_nodos = self.__class__
            nodos_nuevos.append(fabrica_nodos(estado=estado_nuevo,
                                            padre=None if busqueda_local else self,
                                            problema=self.problema,
                                            accion=accion,
                                            costo=self.costo + costo,
                                            profundidad=self.profundidad + 1))
        return nodos_nuevos

    def camino(self):
        '''Camino (lista de nodos y acciones) desde el nodo raiz al nodo actual.'''
        nodo = self
        camino = []
        while nodo:
            camino.append((nodo.accion, nodo.estado))
            nodo = nodo.padre
        return list(reversed(camino))

    def __eq__(self, otro):
        return isinstance(otro, NodoBusqueda) and self.estado == otro.estado

    def estado_representacion(self):
        return self.problema.estado_representacion(self.estado)

    def accion_representacion(self):
        return self.problema.accion_representacion(self.accion)

    def __repr__(self):
        return 'Node <%s>' % self.estado_representacion().replace('\n', ' ')

    def __hash__(self):
        return hash((
            self.estado,
            self.padre,
            self.accion,
            self.costo,
            self.profundidad,
        ))
    
class NodoBusquedaHeuristicaOrdenado(NodoBusqueda):
    def __init__(self, *args, **kwargs):
        super(NodoBusquedaHeuristicaOrdenado, self).__init__(*args, **kwargs)
        self.heuristica = self.problema.heuristica(self.estado)

    def __lt__(self, otro):
        return self.heuristica < otro.heuristica
    
class NodoBusquedaAEstrellaOrdenado(NodoBusquedaHeuristicaOrdenado):
    def __lt__(self, otro):
        return self.heuristica + self.costo < otro.heuristica + otro.costo
    

class ProblemaBusqueda(object):
    '''Clase base abstracta, para representar y manipular los espacio de busqueda
    de un problema. IEn esta clase, el espacio de búsqueda debe representarse 
    implícitamente como un gráfico.
    Cada estado corresponde con un estado del problema(es decir, una configuración válida) 
    y cada accion del problema(es decir, una transformación válida a una configuración) corresponde con un limite o frontera.
    Para utilizar esta clase se debe implementar metodos requeridos by el algoritmo de busqueda
    que se utilizara.'''

    def __init__(self, estado_inicial=None):
        self.estado_inicial = estado_inicial

    def acciones(self, estado):
        '''Devuelve las acciones disponibles para realizar a partir de un estado.
        El valor devuelto es íterador sobre acciones.
        Las acciones son específicas del problema y no se debe asumir nada sobre ellas.
        '''
        raise NotImplementedError

    def resultado(self, estado, accion):
        '''Debuelve un nuevo estado despues de aplicar una accion a estado.'''
        raise NotImplementedError

    def costo(self, estado, accion, estado2):
        '''Devuelve el costo de aplicar una accion para alcanzar el estado2 a partir de estado.
            El valor devuelto es un numero (intero o de punto flotante),
            por defecto la funcion devuelve 1.
        '''
        return 1

    def es_objetivo(self, estado):
        '''Devuelve True si estado es el estado_objetivo y false caso contrario'''
        raise NotImplementedError

    def valor(self, estado):
        '''Devuelve el valor de `estado`, para motivos de optimizacion.
            valor es un numero (entero o punto flotante).'''
        raise NotImplementedError

    def heuristica(self, estado):
        '''DEvuelve un estimado del costo faltante para alcanzar la solucion a partir de `estado`.'''
        return 0

    def estado_representacion(self, estado):
        """
        Devuelve un string de representacion de un estado.
        Por defecto devuelve str(estado).
        """
        return str(estado)

    def accion_representacion(self, accion):
        """
        Devuelve un string de representacion de una acción.
        Por defecto devuelve str(acción).
        """
        return str(accion)
    
def voraz(problema, busqueda_en_grafo=False, viewer=None):
    '''
    Busqueda voraz.

    Si se establece busqueda_en_grafo=True, se eliminara la busqueda en estados repetidos.
    Requiere redefinir las funciones de la clase ProblemaBusqueda:
    ProblemaBusqueda.acciones, ProblemaBusqueda.resultado, y
    ProblemaBusqueda.es_objetivo, ProblemaBusqueda.costo,
    ProblemaBusqueda.heuristica.
    '''
    return _buscar(problema,
                    ColaPrioridadLimitada(),
                    busqueda_en_grafo=busqueda_en_grafo,
                    fabrica_nodos=NodoBusquedaHeuristicaOrdenado,
                    reemplazar_grafo_cuando_mejor=True)

def aestrella(problema, busqueda_en_grafo=False, viewer=None):
    '''
    Busuqeda A*.

    Si se establece busqueda_en_grafo=True, se eliminara la busqueda en estados repetidos.
    Requiere redefinir las funciones de la clase ProblemaBusqueda:
    ProblemaBusqueda.acciones, ProblemaBusqueda.resultado, y
    ProblemaBusqueda.es_objetivo, ProblemaBusqueda.costo,
    ProblemaBusqueda.heuristica.
    '''
    return _buscar(problema,
                    ColaPrioridadLimitada(),
                    busqueda_en_grafo=busqueda_en_grafo,
                    fabrica_nodos=NodoBusquedaAEstrellaOrdenado,
                    reemplazar_grafo_cuando_mejor=True)

def _buscar(problema, frontera, busqueda_en_grafo=False, limite_profundidad=None,
            fabrica_nodos=NodoBusqueda, reemplazar_grafo_cuando_mejor=False):
    '''
    Algoritmo basico de busqueda, base de todos los demas algoritmos de busqueda.
    '''
    memoria = set()
    nodo_inicio = fabrica_nodos(estado=problema.estado_inicial, problema=problema)
    frontera.push(nodo_inicio)

    while frontera:
        nodo = frontera.pop()

        if problema.es_objetivo(nodo.estado):
            return nodo
    
        memoria.add(nodo.estado)

        if limite_profundidad is None or nodo.profundidad < limite_profundidad:
            expandido = nodo.expandir()
    
            for n in expandido:
                if busqueda_en_grafo:
                    otros = [x for x in frontera if x.estado == n.estado]
                    assert len(otros) in (0, 1)
                    if n.estado not in memoria and len(otros) == 0:
                        frontera.push(n)
                    elif reemplazar_grafo_cuando_mejor and len(otros) > 0 and n < otros[0]:
                        frontera.remove(otros[0])
                        frontera.push(n)
                else:
                    frontera.push(n)

import math

MAPA = """
############
#e   # ##  #
# ##       #
# #  #  # ##
##    #   ##
#     ## # #
# ##   #  3#
# #       ##
# # ##### ##
##  1###  2#
############
"""
MAPA = [list(x) for x in MAPA.split("\n") if x]

COSTOS = {
    "arriba": 1.0,
    "abajo": 1.0,
    "izquierda": 1.0,
    "derecha": 1.0,
    "arriba izquierda": 2.0,
    "arriba derecha": 2.0,
    "abajo izquierda": 2.0,
    "abajo derecha": 2.0,
}


class JuegoLaberinto(ProblemaBusqueda):

    def __init__(self, tablero, objetivo):
        self.tablero = tablero
        self.estado_objetivo = (0, 0)
        for y in range(len(self.tablero)):
            for x in range(len(self.tablero[y])):
                if self.tablero[y][x].lower() == "e":
                    self.estado_inicial = (x, y)
                elif self.tablero[y][x].lower() == objetivo:
                    self.estado_objetivo = (x, y)

        super(JuegoLaberinto, self).__init__(estado_inicial=self.estado_inicial)

    def acciones(self, estado):
        acciones = []
        for accion in list(COSTOS.keys()):
            nuevox, nuevoy = self.resultado(estado, accion)
            if self.tablero[nuevoy][nuevox] != "#":
                acciones.append(accion)
        return acciones

    def resultado(self, estado, accion):
        x, y = estado

        if accion.count("arriba"):
            y -= 1
        if accion.count("abajo"):
            y += 1
        if accion.count("izquierda"):
            x -= 1
        if accion.count("derecha"):
            x += 1

        estado_nuevo = (x, y)
        return estado_nuevo

    def es_objetivo(self, estado):
        return estado == self.estado_objetivo

    def costo(self, estado, accion, estado2):
        return COSTOS[accion]

    def heuristic(self, estado):
        x, y = estado
        gx, gy = self.estado_objetivo
        return math.sqrt((x - gx) ** 2 + (y - gy) ** 2)


def main():
#camino1
    problema = JuegoLaberinto(MAPA, "1")
    resultado1 = aestrella(problema, busqueda_en_grafo=True)
    camino1Count = 0
    camino1 = [x[1] for x in resultado1.camino()]
#camino2
    problema2 = JuegoLaberinto(MAPA, "2")
    resultado2 = aestrella(problema2, busqueda_en_grafo=True)
    camino1Count2 = 0
    camino2 = [x[1] for x in resultado2.camino()]
#camino3
    problema3 = JuegoLaberinto(MAPA, "3")
    resultado3 = aestrella(problema3, busqueda_en_grafo=True)
    camino2Count3 = 0
    camino3 = [x[1] for x in resultado3.camino()]

    for y in range(len(MAPA)):
        for x in range(len(MAPA[y])):
            if (x, y) == problema.estado_inicial:
                print("E", end='')
            elif (x, y) == problema.estado_objetivo:
                print("1", end='')

            elif (x, y) == problema2.estado_objetivo:
                print("2", end='')

            elif (x, y) == problema3.estado_objetivo:
                print("3", end='')
                                
            elif (x, y) in camino1:
                print("·", end='')
                camino1Count += 1

            elif (x, y) in camino2:
                print("*", end='')
                camino1Count2 += 1
            
            elif (x, y) in camino3:
                print("+", end='')
                camino2Count3 += 1   
            
            else:
                print(MAPA[y][x], end='')
        print()

    print("recorrido del camino1: ", len(camino1))
    print("recorrido del camino2: ", len(camino2))
    print("recorrido del camino3: ", len(camino3))

    if camino1 < camino2 and camino1 < camino3:
        print("El mejor camino es: 1 -> S1")
    elif camino2 < camino1 and camino2 < camino3:
        print("El mejor camino es: 2 -> S2")
    elif camino3 < camino2 and camino3 < camino1:
        print("El mejor camino es: 3 -> S3")
    else:
        print("son iguales")
        
    


if __name__ == "__main__":
    main()