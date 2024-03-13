from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('sign-out/', views.sign_out, name='sign_out'),
    
    path('route/', views.route, name = 'route'),
    path('function/', views.function, name = 'function'),
    path('map/', views.map , name = 'map'),
    
    path('add-staff/', views.add_staff, name = 'add_staff'),
    path('update-staff/<id>/', views.update_staff, name = 'update_staff'),
    path('delete-staff/<id>/', views.delete_staff, name = 'delete_staff'),
    path('staff/', views.staff, name = 'staff'),

    path('add-brigade/<id>/', views.add_brigade, name = 'add_brigade'),
    path('update-brigade/<id>/', views.update_brigade, name = 'update_brigade'),
    path('delete-brigade/<id>/', views.delete_brigade, name = 'delete_brigade'),
    path('brigade/', views.brigade, name = 'brigade'),
    
    path('add-map/', views.add_map, name = 'add_map'),
    path('update-map/<id>/', views.update_map, name = 'update_map'),
    path('delete-map/<id>/', views.delete_map, name = 'delete_map'),
    path('maps/', views.maps, name = 'maps'),


    path('add-node/', views.add_node, name = 'add_node'),
    path('update-node/<id>/', views.update_node, name = 'update_node'),
    path('delete-node/<id>/', views.delete_node, name = 'delete_node'),
    path('node/', views.node, name = 'node'),
    
    path('add-graph/', views.add_graph, name = 'add_graph'),
    path('update-graph/<id>/', views.update_graph, name = 'update_graph'),
    path('delete-graph/<id>/', views.delete_graph, name = 'delete_graph'),
    path('graph/', views.graph, name = 'graph'),
    path('graph/mapa', views.graph_map, name = 'graph_map'),
    path('graph/shape', views.graph_node, name = 'graph_node'),

    path('geo/', views.geo, name='geo'),

    path('all-staff/', views.get_staff, name='all_staff'),

    path('routes/<faculty>/', views.faculty),
    
    # restablecer contraseña urls
    path('reset/', views.send_email_reset_password, name='send_email_reset_password'),
    path('reset-password/<email>', views.reset_password, name='reset-password'),
    path('reset-msg/', views.reset_msg, name='reset-msg'),
    
    # simulación urls
    path('simulation/', views.simulation_route, name='simulation-route'),
    
]

