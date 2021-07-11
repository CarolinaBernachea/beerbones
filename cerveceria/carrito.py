from decimal import Decimal
from django.conf import settings
from cerveceria.models import Producto

"""
	Se implementa un carrito de compras utilizando de base la guía que aparece
	en el libro "Django 3 by Example" de Antonio Mele.
	El Carrito es único para cada sesión que exista en la página.
	Se implementa como una clase con todos los métodos que se necesitan para 
	poder usarlo en la página.
"""


class Carrito(object):
	# Inicio el Carrito
	def __init__(self, request):
		self.session = request.session
		carrito = self.session.get(settings.CARRITO_SESSION_ID)
		if not carrito:
			# Guardar un carrito vacío en la sesión
			carrito = self.session[settings.CARRITO_SESSION_ID] = {}
		self.carrito = carrito

	# 'add' y 'save': Añadir un producto al carrito o actualizar su cantidad
	def agregar(self, producto, cantidad=1, override_cantidad = False):
		producto_id = str(producto.id)
		if producto_id not in self.carrito:
			self.carrito[producto_id] = {'cantidad': 0,
									  	'precio': str(producto.precio)}
		if override_cantidad:
			self.carrito[producto_id]['cantidad'] = cantidad
		else:
			self.carrito[producto_id]['cantidad'] += cantidad
		self.save()

	# Marca a la sesión como modificada para que Django la guarde
	def save(self):
		self.session.modified = True

	# Elimina un producto del carrito
	def remover(self, producto):
		producto_id = str(producto.id)
		if producto_id in self.carrito:
			del self.carrito[producto_id]
			self.save()

	# Itera entre los elementos en 'carrito' y obtiene los productos
	# desde la bbdd
	def __iter__(self):
		ids_producto = self.carrito.keys()
		productos = Producto.objects.filter(id__in = ids_producto)
		carrito =  self.carrito.copy()
		for producto in productos:
			carrito[str(producto.id)]['producto'] = producto
		for item in carrito.values():
			item['precio'] = Decimal(item['precio'])
			item['precio_total'] = item['precio'] * item['cantidad']
			yield item

	# Cuenta los item en el carrito		
	def __len__(self):
		return sum(item['cantidad'] for item in self.carrito.values())

	# Trae el precio total
	def get_precio_total(self):
		return sum(Decimal(item['precio']) * item['cantidad'] for item in self.carrito.values())

	# Elimina el carrito de la sesión actual
	def clear(self):
		del self.session[settings.CARRITO_SESSION_ID]
		self.save()


def carrito(request):
	return {'carrito': Carrito(request)}