from .models import Node, Connection
import heapq, math


def dijkstra(nodes, connections, start, end):

    distances = {node.name: float('infinity') for node in nodes}
    distances[start] = 0

    priority_queue = [(0, start)]

    while priority_queue:
        current_distance, current_node_name = heapq.heappop(priority_queue)

        if current_distance > distances[current_node_name]:
            continue

        current_node = next(node for node in nodes if node.name == current_node_name)

        for connection in connections:
            if connection.source == current_node:
                new_distance = distances[current_node_name] + connection.weight

                if new_distance < distances[connection.destination.name]:
                    distances[connection.destination.name] = new_distance
                    heapq.heappush(priority_queue, (new_distance, connection.destination.name))

    if distances[end] == float('infinity'):
        return [], float('infinity')

    path = []
    current_node_name = end

    while current_node_name != start:
        found_connection = False

        for connection in connections:
            if connection.destination.name == current_node_name and distances[current_node_name] - connection.weight == distances[connection.source.name]:
                path.insert(0, connection.source.name)
                current_node_name = connection.source.name
                found_connection = True
                break

        if not found_connection:
            return [], float('infinity')

    path.append(end)
    return path, distances[end]


def search_path(lat, lon):

    nodes = Node.objects.all()

    connections = Connection.objects.all()

    start_node = close_node(lat, lon, nodes).name

    end_nodes = safe_zones(nodes)

    print(start_node, end_nodes)

    shortest_path, total_weight = dijkstra(nodes, connections, start_node, end_nodes[0])
    print('NO paso de aca')

    for node in end_nodes[1:]:
        current_path, current_weight = dijkstra(nodes, connections, start_node, node)
        if current_weight < total_weight:
            shortest_path, total_weight = current_path, current_weight

    return shortest_path


def safe_zones(list_nodes):

    nodes_safe = []

    for node in list_nodes:
        if node.is_safe == 's':
            nodes_safe.append(node.name)
    
    return nodes_safe


def distance(la1, lo1, la2, lo2):
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


def close_node(lat, lon, nodes):

    total = float('inf')

    result = nodes[0]

    for node in nodes:

        dst = distance(lat, lon, node.latitude, node.longitude)
        if total > dst:
            result = node
            total = dst

    return result