from django.shortcuts import render, redirect, get_object_or_404
from .models import Node, Brigade, FunctionsBrigade, Staff, Connection, Map
from .forms import FormFunctionsBrigade, MapForm, NodeForm, FormConnection, StaffForm, EmailForm, PasswordForm
import folium
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .graph import calculate_route
from django.http import JsonResponse

def index(request):
    
    if request.method == 'POST':
        sign_in(request)
    
    return render(request, 'index.html')

# Calcular Ruta de Evacuación
def route(request):

    if request.method == 'POST':
        sign_in(request)
    
    # obtener ubicación del usuario
    lat = float(request.GET.get('latitude')) # latitud 
    lon = float(request.GET.get('longitude')) # longitud
    
    # descomentar esto para pruebas simulación, y comentar lo de arriba para evitar problemas
    #lat = -4.032736
    #lon = -79.199834
    
    path_nodes = [] # camino(array de nodos)

    route_nodes, distance = calculate_route(lat, lon)
    
    # verificar si existe una ruta de evacuación
    if not route_nodes:
        return render(request, 'no-route.html')

    # llenando el camino(array de nodos)
    for node in route_nodes:
        # consultando los nodos en la base de datos
        path_nodes.append(Node.objects.get(name=node))


    # inicializar mapa, usando la ubicación(lat, lon) del usuario
    initial_map = folium.Map(location=[lat,lon], zoom_start=19)

    # inicializar destino(zona segura)
    end_node = path_nodes[-1]

    # agregar marker en el mapa de la ubicación del usuario
    folium.Marker(location=[lat, lon], popup="Tu ubicación", icon=folium.Icon(color='red', icon='')).add_to(initial_map)
    
    # agregar marker en el mapa del destino(zona segura)
    folium.Marker(location=[end_node.latitude, end_node.longitude], popup=end_node.name, icon=folium.Icon(color='green', icon='')).add_to(initial_map)

    # agregar markers de los nodos intermediarios
    for middle_node in path_nodes[0:-1]:
        folium.Marker(location=[middle_node.latitude, middle_node.longitude], popup=middle_node.name, icon=folium.Icon(color='blue')).add_to(initial_map)

    # inicializo la ruta en un arreglo para el mapa
    route_coordinates = [(lat, lon)]
    route_coordinates += [(node.latitude, node.longitude) for node in path_nodes]

    # agregar ruta al mapa
    folium.PolyLine(locations=route_coordinates, color='#86B6F6', weight=8).add_to(initial_map)

    # agregar variables para el template
    context = {
        'map': initial_map._repr_html_(),
        'start': "Tu ubicación",
        'middle': path_nodes[0:-1],
        'end': end_node,
        'distance': round(distance)
    }

    return render(request, 'route.html', context)

# Simular rutas de evacuación
def simulation_route(request):
    
    lat = -4.034000
    lon = -79.202136 
    
    nodes = Node.objects.exclude(name__icontains='aux')
    
    initial_map = folium.Map(location=[lat,lon], zoom_start=17)

    context = {
        'nodes': nodes,
    }

    if request.method == 'POST':
        
        node_start = get_object_or_404(Node, id= request.POST.get('nodo'))

        lat = node_start.latitude
        lon = node_start.longitude
        
        path_nodes = []

        route_nodes, distance = calculate_route(lat, lon)
        
        for node in route_nodes:
            path_nodes.append(Node.objects.get(name=node))

        initial_map = folium.Map(location=[lat,lon], zoom_start=19)

        end_node = path_nodes[-1]

        folium.Marker(location=[lat, lon], popup="Tu ubicación", icon=folium.Icon(color='red', icon='')).add_to(initial_map)
        folium.Marker(location=[end_node.latitude, end_node.longitude], popup=end_node.name, icon=folium.Icon(color='green', icon='')).add_to(initial_map)

        for middle_node in path_nodes[1:-1]:
            folium.Marker(location=[middle_node.latitude, middle_node.longitude], popup=middle_node.name, icon=folium.Icon(color='blue')).add_to(initial_map)

        route_coordinates = [(lat, lon)]

        route_coordinates += [(node.latitude, node.longitude) for node in path_nodes]

        folium.PolyLine(locations=route_coordinates, color='#86B6F6', weight=8).add_to(initial_map)
        
        context['start'] = "Tu Ubicación"
        context['middle'] = path_nodes[1:-1]
        context['end'] = end_node
        context['distance'] = round(distance)

    context['map'] = initial_map._repr_html_()
    
    return render(request, 'admin/simulation/simulation.html', context)

# improve presentation
def function(request):
    
    if request.method == 'POST':
        sign_in(request)
    
    brigades = Brigade.objects.all()
    
    functions = FunctionsBrigade.objects.order_by('function')
    
    context = {
        'brigades': brigades,
        'functions_brigades': functions
    }
    
    return render(request, 'brigade.html', context)

def map(request):
    
    if request.method == 'POST':
        sign_in(request)
    
    maps = Map.objects.all()
    
    context = {
        'maps': maps,
    }
    
    return render(request, 'map.html', context)

def sign_in(request):
    
    username = request.POST.get('username')
    password = request.POST.get('password')
    
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        login(request, user)
        return redirect('index')
    
    messages.error(request, "Los valores no son validos")
    return redirect('index')

def sign_out(request):
    logout(request)
    return redirect('index')

# Brigade Crud

@login_required
def brigade(request):
    query = request.GET.get('search_name', '')
    page = request.GET.get('page', 1)
    brigades = Brigade.objects.all()
    
    try:
        paginator = Paginator(brigades, 10)
        brigades = paginator.page(page)
    except:
        raise Http404

    if query:
        brigades = Brigade.objects.filter(name__icontains=query)        
    
    context = {
        'items': brigades,
        'paginator': paginator,
    }

    return render(request, 'admin/brigade/brigade.html', context)

@login_required
def add_brigade(request, id):

    brigade = Brigade.objects.get(id=id)

    functions = FunctionsBrigade.objects.filter(brigade=id).order_by('function')

    context = {
        "form": FormFunctionsBrigade(initial={'brigade': brigade}),
        "items": functions,
        "brigade": brigade,
    }

    if request.method == 'POST':
        form_function = FormFunctionsBrigade(data = request.POST)
        if form_function.is_valid():
            form_function.save()
            messages.success(request, "Guardado correctamente")
            return redirect('add_brigade', brigade.id)
        else:
            messages.error(request, "Error al guardar")
            return redirect('add_brigade', brigade.id)
    
    return render(request, 'admin/brigade/add.html', context)

@login_required
def update_brigade(request, id):

    function = get_object_or_404(FunctionsBrigade ,id=id)

    brigade = Brigade.objects.get(id=function.brigade.id)

    functions = FunctionsBrigade.objects.filter(brigade=function.brigade)

    context = {
        "form": FormFunctionsBrigade(instance=function),
        "items": functions,
        "brigade": brigade,
    }
    
    if request.method == 'POST':
        form_function = FormFunctionsBrigade(data=request.POST, instance=function)
        
        print(form_function)

        if form_function.is_valid():
            form_function.save()
            messages.success(request, "Actualizado correctamente")
            return redirect('add_brigade', brigade.id)
        else:
            messages.error(request, "Error al actualizar")
            return redirect('add_brigade', brigade.id)

    return render(request, 'admin/brigade/add.html', context)

@login_required
def delete_brigade(request, id):

    function = get_object_or_404(FunctionsBrigade, id=id)

    brigade = Brigade.objects.get(id=function.brigade.id)
    
    function.delete()
    
    messages.success(request, "Eliminado correctamente")
    
    return redirect('add_brigade', brigade.id)

# Staff Crud
@login_required
def add_staff(request):
    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Guardado correctamente")
            return redirect('staff')
    else:
        form = StaffForm()

    return render(request, 'add.html', {'form': form, 'btn': 'Agregar'})

@login_required
def update_staff(request, id):
    if id:
        staff = get_object_or_404(Staff, id=id)
    else:
        staff = None

    if request.method == 'POST':
        form = StaffForm(request.POST, instance=staff)
        if form.is_valid():
            form.save()
            messages.success(request, "Actualizado correctamente")
            return redirect('staff')
    else:
        form = StaffForm(instance=staff)

    return render(request, 'add.html', {'form': form, 'btn': 'Actualizar'})

@login_required
def delete_staff(request, id):
    
    staff = get_object_or_404(Staff, id=id)
    
    staff.delete()
    
    messages.success(request, "Eliminado correctamente")
    
    return redirect('staff')

@login_required
def staff(request):
    query = request.GET.get('search_name', '')
    page = request.GET.get('page', 1)
    staff = Staff.objects.all()
    
    try:
        paginator = Paginator(staff, 10)
        staff = paginator.page(page)
    except:
        raise Http404

    if query:
        staff = Staff.objects.filter(name__icontains=query)        
    
    context = {
        'items': staff,
        'paginator': paginator,
    }
    
    return render(request, 'admin/staff/staff.html', context)

# Crud Node
@login_required
def node(request):
    print("a")
    query = request.GET.get('search_name', '')
    page = request.GET.get('page', 1)
    node = Node.objects.all()
    
    try:
        paginator = Paginator(node, 20)
        node = paginator.page(page)
    except:
        raise Http404

    if query:
        node = Node.objects.filter(name__icontains=query)        
    
    contex = {
        'items': node,
        'paginator': paginator,
    }
    
    return render(request, 'admin/node/node.html', contex)

@login_required
def add_node(request):
    if request.method == 'POST':
        form = NodeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Guardado correctamente")
            return redirect('node')
    else:
        form = NodeForm()

    return render(request, 'admin/node/add.html', {'form': form, 'btn': 'Agregar'})

@login_required
def delete_node(request, id):
    
    node = get_object_or_404(Node, id=id)
    
    node.delete()
    
    messages.success(request, "Eliminado correctamente")
    
    return redirect('node')

@login_required
def update_node(request, id):
    if id:
        node = get_object_or_404(Node, id=id)
    else:
        node = None

    if request.method == 'POST':
        form = NodeForm(request.POST, instance=node)
        if form.is_valid():
            form.save()
            messages.success(request, "Actualizado correctamente")
            return redirect('node')
    else:
        form = NodeForm(instance=node)

    return render(request, 'admin/node/add.html', {'form': form, 'btn': 'Actualizar'})

# Crud Graph
@login_required
def graph(request):
    
    query = request.GET.get('search_name', '')
    page = request.GET.get('page', 1)
    graph = Connection.objects.all()
    
    edges, nodes = init_graph()
    
    try:
        paginator = Paginator(graph, 20)
        graph = paginator.page(page)
    except:
        raise Http404

    if query:
        graph = Connection.objects.filter(source__name__startswith=query)       
    
    context = {
        'items': graph,
        'paginator': paginator,
        'nodes': nodes,
        'edges': edges,
    }
    
    return render(request, 'admin/graph/graph.html', context)

@login_required
def graph_map(request):
    
    lat = -4.032863
    lon = -79.201807
    
    nodes = Node.objects.all()
    connections = Connection.objects.all()

    my_map = folium.Map(location=[lat, lon], zoom_start=17)

    for node in nodes:
        folium.Marker(
            location=[node.latitude, node.longitude],
            popup=node.name,
            icon=folium.Icon(color='green' if node.is_safe == 's' else 'blue')
        ).add_to(my_map)

    for connection in connections:
        src_node = Node.objects.get(pk=connection.source_id)
        dest_node = Node.objects.get(pk=connection.destination_id)
        folium.PolyLine(
            locations=[
                [src_node.latitude, src_node.longitude],
                [dest_node.latitude, dest_node.longitude]
            ],
            color='black',
            weight=3    
        ).add_to(my_map)
    
    context = {'map': my_map._repr_html_()}
    
    return render(request, 'admin/graph/map-graph.html', context)

@login_required
def graph_node(request):
    
    nodos = Node.objects.all()
    aristas = Connection.objects.all()

    edges = []
    nodes = []

    for nodo in nodos:
        nodes.append({'id': nodo.name, 'label': nodo.name})

    added_connections = set()

    for arista in aristas:
        
        connection_key = frozenset([arista.source.name, arista.destination.name])
        
        if connection_key not in added_connections:
            edges.append({'from': arista.source.name, 'to': arista.destination.name, 'label': f'{round(arista.weight, 2)}'})
            added_connections.add(connection_key)
    
    context = {
        'nodos': nodes,
        'aristas': edges,
    }
    
    return render(request, 'admin/graph/node-graph.html', context)    

@login_required
def add_graph(request):
    
    context = {
        "form": FormConnection()
    }
    
    if request.method == 'POST':
        form_connection = FormConnection(data = request.POST)
        if form_connection.is_valid():
            form_connection.save()
            messages.success(request, "Guardado correctamente")
            return redirect('graph')
        else:
            messages.error(request, "Error al guardar")
            return redirect('graph')
            
    return render(request, 'admin/graph/add.html', context)

@login_required
def delete_graph(request, id):
    
    connection = get_object_or_404(Connection, id=id)
    
    connection.delete()
    
    messages.success(request, "Eliminado correctamente")
    
    return redirect('graph')

@login_required
def update_graph(request, id):
    
    connection = get_object_or_404(Connection, id=id)
    
    context = {'form': FormConnection(instance=connection)}
    
    if request.method == 'POST':
        form_connection = FormConnection(data=request.POST, instance=connection)
        
        if form_connection.is_valid():
            form_connection.save()
            messages.success(request, "Actualizado correctamente")
            return redirect('graph')
        else:
            messages.error(request, "Error al actualizar")
            return redirect('graph')
    
    return render(request, 'admin/graph/add.html', context)

@login_required
def init_graph():
    
    nodos = Node.objects.all()
    aristas = Connection.objects.all()

    edges = []
    nodes = []

    for nodo in nodos:
        nodes.append({'id': nodo.name, 'label': nodo.name})

    added_connections = set()

    for arista in aristas:
        
        connection_key = frozenset([arista.source.name, arista.destination.name])
        
        if connection_key not in added_connections:
            edges.append({'from': arista.source.name, 'to': arista.destination.name, 'label': f'{round(arista.weight, 2)}'})
            added_connections.add(connection_key)
    
    return edges, nodes

# Crud Map
@login_required
def add_map(request):
    if request.method == 'POST':
        form = MapForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Guardado correctamente")
            return redirect('maps')
    else:
        form = MapForm()

    return render(request, 'admin/map/add.html', {'form': form, 'btn': 'Agregar'})

@login_required
def update_map(request, id):
    
    if id:
        mapita = get_object_or_404(Map, id=id)
    else:
        mapita = None

    if request.method == 'POST':
        form = MapForm(request.POST, request.FILES, instance=mapita)
        if form.is_valid():
            form.save()
            messages.success(request, "Actualizado correctamente")
            return redirect('maps') 
    else:
        form = MapForm(instance=mapita)
        
    return render(request, 'admin/map/add.html', {'form': form, 'btn': 'Actualizar'})

@login_required
def maps(request):
    conext = {
        'maps': Map.objects.all()
    }

    return render(request, 'admin/map/map.html', conext)

@login_required
def delete_map(request, id):
    
    mapita = get_object_or_404(Map, id=id)
    
    mapita.delete()
    
    messages.success(request, "Eliminado correctamente")
    
    return redirect('maps')

# geolocation
def geo(request):
    return render(request, 'geo.html')

# API

def get_staff(request):
    # , , ,  y 
    # si es un profesor solo se le manda el link de geo
    # si es brigadita se le manda solo los puntos de zonas seguras

    staff_data = list(Staff.objects.values())  # Obtener todos los datos del modelo Staff
    return JsonResponse(staff_data, safe=False)

def faculty(request, faculty):
    
    nodes_safe = Node.objects.filter(is_safe='s', name__icontains=faculty)
    
    initial_map = folium.Map(location=[nodes_safe[0].latitude,nodes_safe[0].longitude], zoom_start=18)
    
    for node in nodes_safe:
        folium.Marker(location=[node.latitude, node.longitude], popup=node.name, icon=folium.Icon(color='green')).add_to(initial_map)
    
    context = {
        'map': initial_map._repr_html_(),
        'nodes': nodes_safe,
    }
    
    return render(request, 'faculty.html', context)


# Restablecer contraseña

from django.core.mail import EmailMessage
from django.conf import settings

def send_email_reset_password(request):
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            to_email = form.cleaned_data['email']
            body = 'iHola! \nHola, se solicitó un restablecimiento de contraseña para tu cuenta haz clic en el link que aparece a continuación para cambiar tu contraseña.\n'
            email = EmailMessage(
                'Restablecer contraseña',
                body + f'http://127.0.0.1:8000/reset-password/{to_email}',
                settings.EMAIL_HOST_USER,
                [to_email]
            )
            
            email.fail_silently = False
            
            email.send()
            
            return redirect('reset-msg')
    else:
        form = EmailForm()

    return render(request, 'reset-password.html', {'form': form})

def reset_password(request, email):
    if email:
        user = get_object_or_404(User, email=email)
    else:
        user = None
    
    if request.method == 'POST':
        form = PasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['password']
            user.set_password(new_password)
            user.save()
            messages.success(request, "Contraseña Actualizada")
            return redirect('index')
    else:
        form = PasswordForm()

    return render(request, 'reset.html', {'form': form})

def reset_msg(request):
    return render(request, 'reset-msg.html')