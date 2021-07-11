from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from cerveceria.models import *
from cerveceria.forms import *
from django import forms
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from cerveceria.carrito import Carrito


def index(request):
    return render(request, 'index.html')


def buscar(request):
	if "busca" in request.GET and request.GET["busca"]:
		consulta = request.GET["busca"]
		keyword = "{}".format(request.GET["busca"])
		cerveceria = Producto.objects.filter(cerveceria__nombre__icontains = consulta)
		pais = Producto.objects.filter(cerveceria__pais__icontains = consulta)
		variedad = Producto.objects.filter(variedad__icontains = consulta)
		nombre_comercial = Producto.objects.filter(nombre_comercial__icontains = consulta)
		# concateno los query sets con | para buscar por varios criterios
		formulario_agregar_carrito = AgregarAlCarritoForm()
		return render(request, "resultados.html",{"res":cerveceria | variedad | 
						pais | nombre_comercial, "busca": keyword,
						'formulario_agregar_carrito': formulario_agregar_carrito }) 
	else:
		return render(request, "resultados.html")


def catalogo(request):
	todos_prod = Producto.objects.all()
	formulario_agregar_carrito = AgregarAlCarritoForm()
	return render(request, "catalogo.html", {"catalogo": todos_prod,
											'formulario_agregar_carrito': formulario_agregar_carrito})


def contacto(request):
	if request.method == "POST": #método POST no muestra en la barra lo que busco
		formulario = ContactoForm(request.POST)
		if formulario.is_valid():
			nombre = formulario.cleaned_data["nombre"]
			asunto = formulario.cleaned_data["asunto"]
			mail_rtte = formulario.cleaned_data["correo"]
			body = formulario.cleaned_data["mensaje"]
			mensaje = "De: {} <{}> \n\n{}".format(nombre, mail_rtte, body)
			correo = EmailMessage(subject = asunto, body = mensaje, reply_to = [mail_rtte], to =["cerveceriabeerbones@gmail.com"])
			try:
				correo.send()
				return render(request, "contacto.html", {'formulario': formulario, 'correo_enviado' : True})
			except:
				return render (request, "contacto.html", {'formulario': formulario, 'correo_enviado' : False})
	else:
		formulario = ContactoForm()
		return render(request, 'contacto.html', {'formulario': formulario})


# Además del 'User', se registra al 'Cliente', todo a la vez.
def registro(request):
	if request.method == 'POST':
		formulario = RegistroForm(request.POST)
		if formulario.is_valid():
			user = formulario.save()
			user.refresh_from_db()
			user.cliente.nombre = formulario.cleaned_data.get('nombre')
			user.cliente.apellido = formulario.cleaned_data.get('apellido')
			user.cliente.direccion = formulario.cleaned_data.get('direccion')
			user.cliente.telefono = formulario.cleaned_data.get('telefono')
			user.cliente.email = formulario.cleaned_data.get('email')
			user.save()
			#luego de registrarse se loguea automáticamente
			password_ingresado = formulario.cleaned_data.get('password1')
			user = authenticate(username=user.username, password=password_ingresado)
			login(request, user)
			return render(request, "registro.html", {'formulario': formulario, 
													 'usuario_creado' : True})
		else:
			return render(request, "registro.html", {'formulario': formulario,
													 'usuario_creado' : False})
	else:
		formulario = RegistroForm()
		return render(request, "registro.html", {'formulario': formulario})


def salir(request):
	logout(request)
	return HttpResponseRedirect("/")


def error_404(request, exception):
	response = render(request, '404.html', {})
	return response


def error_500(request):
	response = render(request, '500.html', {})
	return response



# Vistas del carrito

@require_POST
def agregar_al_carrito(request, producto_id):
	carrito = Carrito(request)
	producto = get_object_or_404(Producto, id = producto_id)
	formulario = AgregarAlCarritoForm(request.POST)
	if formulario.is_valid():
		cd = formulario.cleaned_data
		carrito.agregar(producto = producto,
					cantidad = cd['cantidad'],
					override_cantidad = cd['override'])
	return redirect('detalle_carrito')


@require_POST
def eliminar_de_carrito(request, producto_id):
	carrito = Carrito(request)
	producto = get_object_or_404(Producto, id = producto_id)
	carrito.remover(producto)
	return redirect('detalle_carrito')

				
def detalle_carrito(request):
	carrito = Carrito(request)
	for item in carrito:
		item['form_actualizar_cant'] = AgregarAlCarritoForm(initial={'cantidad': item['cantidad'],
																	'override': True})
	return render(request, 'detalle.html', {'carrito': carrito})


# esta función envía un mail tanto al cliente como al mail de contacto de la página
def enviar_email(request, pedido):
	carrito = Carrito(request)
	print('print1')
	asunto = "Pedido #{}".format(pedido)
	#datos del cliente
	user = request.user
	nombre = user.cliente.nombre
	apellido = user.cliente.apellido
	direccion = user.cliente.direccion
	telefono = user.cliente.telefono
	email = user.cliente.email
	datos_cliente = "<h4><u>Datos del cliente:</u></h4>\
					<p><b>Nombre:</b> {} {}</p>\
					<p><b>Dirección:</b> {}</p>\
					<p><b>Teléfono:</b> {}</p>\
					<p><b>Correo:</b> {}</p>\
					<br><br>".format(nombre,apellido,direccion,telefono,email)
	#detalle del pedido
	mensaje = datos_cliente + "<h4><u>Detalles del pedido:</u></h4>"
	for item in carrito:
		producto = item['producto']
		cantidad = item['cantidad']
		precio_total = item['precio_total']
		total = carrito.get_precio_total()
		
		# se usa for para insertar los guiones que faltan y así cada renglón tiene 
		# el mismo largo y los precios quedan alineados, para lograrlo se usa una fuente monospace.
		largo = len(str(producto)+str(cantidad))
		guiones = ""
		for i in range(50-largo):
			guiones = guiones + "-"
		mensaje = mensaje + "<p>{}  x  {}{}${}</p>".format(cantidad, producto, guiones, precio_total)
	
	#se unen los datos en el cuerpo del correo
	guiones_total = ""
	for i in range(48):
		guiones_total = guiones_total + "-"
	mensaje = mensaje + "<p><b>TOTAL</b>{}<b>${}</b></p>".format(guiones_total, total)
	mensaje = '<font face="Consolas, Courier, monospace">' + mensaje + '</font>'
	correo = EmailMessage(subject=asunto, body=mensaje, to=["cerveceriabeerbones@gmail.com", email])
	correo.content_subtype = "html"
	print('print2')
	print(correo)
	correo.send()
	print('print3')


@login_required(login_url='/ingresar')
def crear_pedido(request):
	carrito = Carrito(request)
	if request.method == 'POST':
		formulario = CrearPedidoForm(request.POST)
		if formulario.is_valid():
			pedido = formulario.save()
			for item in carrito:
				DetallePedido.objects.create(pedido = pedido,
											producto = item['producto'],
											precio = item['precio'],
											cantidad = item['cantidad'])
			try:
				print('ACA ENTRÓ 1')
				enviar_email(request, pedido)
				print('ACA ENTRÓ 2')
				#limpio el carrito
				carrito.clear()
				return render(request, 'pedido_creado.html', {'pedido': pedido})
			except:
				return render(request, "crear_pedido.html", {'carrito': carrito,
															'formulario': formulario, 
															'pedido_exitoso' : False})
	else:
		formulario = CrearPedidoForm()
	return render(request, 'crear_pedido.html', {'carrito': carrito,
												'formulario': formulario}) 
 

