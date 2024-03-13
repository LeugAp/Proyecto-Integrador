import sys
from .models import Node, Connection
import math

# Clase grafo 
class Graph(object):
    def __init__(self, nodes, init_graph):
        self.nodes = nodes
        self.graph = self.construct_graph(nodes, init_graph)
        
    def construct_graph(self, nodes, init_graph):

        graph = {}
        for node in nodes:
            graph[node] = {}
        
        graph.update(init_graph)
        
        for node, edges in graph.items():
            for adjacent_node, value in edges.items():
                if graph[adjacent_node].get(node, False) == False:
                    graph[adjacent_node][node] = value
                    
        return graph
    
    def get_nodes(self):
        return self.nodes
    
    def get_outgoing_edges(self, node):
        connections = []
        for out_node in self.nodes:
            if self.graph[node].get(out_node, False) != False:
                connections.append(out_node)
        return connections
    
    def value(self, node1, node2):
        return self.graph[node1][node2]


# verifica que zona segura tiene la ruta mas cercana y retorna la ruta
def print_result(previous_nodes, shortest_path, start_node, target_nodes):

    target_node = target_nodes[0]

    for node in target_nodes:
        if(shortest_path[node] < shortest_path[target_node]):
            target_node = node

    path = []
    node = target_node
    distance = shortest_path[node]
    
    while node != start_node:
        path.append(node)
        node = previous_nodes[node]
 
    path.append(start_node)
    
    return reversed(path), distance


# algortimo de busqueda 
def dijkstra_algorithm(graph, start_node):
    unvisited_nodes = list(graph.get_nodes())
 
    shortest_path = {}
 
    previous_nodes = {}
 
    max_value = sys.maxsize
    for node in unvisited_nodes:
        shortest_path[node] = max_value

    shortest_path[start_node] = 0
    
    while unvisited_nodes:
        current_min_node = None
        for node in unvisited_nodes:
            if current_min_node == None:
                current_min_node = node
            elif shortest_path[node] < shortest_path[current_min_node]:
                current_min_node = node
                
        neighbors = graph.get_outgoing_edges(current_min_node)
        for neighbor in neighbors:
            tentative_value = shortest_path[current_min_node] + graph.value(current_min_node, neighbor)
            if tentative_value < shortest_path[neighbor]:
                shortest_path[neighbor] = tentative_value
                previous_nodes[neighbor] = current_min_node
 
        unvisited_nodes.remove(current_min_node)
    
    return previous_nodes, shortest_path


# Construye el grafo con los valores de la base de datos
def init_graph(latitude, longitude, all_nodes):
    
    all_connection = Connection.objects.all()
    
    nodes = []

    for node in all_nodes:
        nodes.append(node.name)

    graph = {}

    for node in all_nodes:
        graph[node.name] = {}
    
    for conex in all_connection:
        graph[conex.source.name][conex.destination.name] = conex.weight
        
    return Graph(nodes, graph)
    

# calcular las rutas mas cercanas de una coordenada hacia las zonas seguras
def calculate_route(latitude, longitude):
    
    all_nodes = Node.objects.all()

    start = close_node(latitude, longitude, all_nodes)
    
    if start is None:
        return [], 0

    graph= init_graph(latitude, longitude, all_nodes)
    
    previous_nodes, shortest_path = dijkstra_algorithm(graph=graph, start_node=start)

    return print_result(previous_nodes, shortest_path, start_node=start, target_nodes=safe_zones())

# recupera los nodos que sean zonas seguras
def safe_zones():
    return [node.name for node in Node.objects.filter(is_safe='s')]

# calcula la distancia de una coordenada a otra
def distance_nodes(la1, lo1, la2, lo2):
    lat1, lon1 = la1, lo1
    lat2, lon2 = la2, lo2
    rad = math.pi / 180 
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = (math.sin(rad * dlat / 2) ** 2) + math.cos(rad * lat1) * math.cos(rad * lat2) * (math.sin(rad * dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    r = 6371
    distancia = r * c
    return distancia * 1000

# Recupera el nodo mas cercano a una ubicación dada(latitud, longitud)
def close_node(lat, lon, nodes):
    
    total = float('inf')

    result = nodes[0]

    for node in nodes:

        dst = distance_nodes(lat, lon, node.latitude, node.longitude)
        if total > dst:
            result = node
            total = dst

    if total >= 100:
        return None
    
    return result.name