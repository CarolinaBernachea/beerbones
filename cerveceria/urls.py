from django.urls import path
from django.contrib.auth.views import LoginView
from django.conf.urls import handler404, handler500
from cerveceria.views import *
from cerveceria.carrito import Carrito

handler404 = error_404
handler500 = error_500

urlpatterns = [
    path('', index, name = 'index'),
    path('busqueda/', buscar, name = 'buscar'),
    path('productos/', catalogo, name = 'productos'),
    path('contacto/', contacto, name = 'contacto'),
    path('registro/', registro, name = 'registro'),
    path('ingresar/', LoginView.as_view(template_name = 'ingresar.html'), name = "login"),
    path('salir/', salir, name = 'salir'),
    path('detalle/', detalle_carrito, name = 'detalle_carrito'),
    path('agregar/<int:producto_id>/', agregar_al_carrito, name = 'agregar_al_carrito'),
    path('remover/<int:producto_id>/', eliminar_de_carrito, name = 'eliminar_de_carrito'),
    path('crear_pedido/', crear_pedido, name = 'crear_pedido'),
]
