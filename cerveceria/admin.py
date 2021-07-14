from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from cerveceria.models import *

# Register your models here.

"""
   Con la siguiente clase puedo anidar los registros de 
   "DetallePedidos" en "Pedidos"
"""


class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    can_delete = False


class PedidoAdmin(admin.ModelAdmin):
    inlines = [DetallePedidoInline,	]
    list_display = ("pedido_id", "cliente", "fecha", "pagado")
    search_fields = ("id", "cliente__nombre", "cliente__apellido")
    list_filter = ["fecha", "pagado"]


"""
   Para que aparezcan los datos de "Cliente" en la vista de usuarios.
"""


class ClienteInline(admin.StackedInline):
    model = Cliente
    can_delete = False


class UserAdmin(BaseUserAdmin):
    inlines = (ClienteInline,)


class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "apellido", "telefono",
                    "user", "email", "pedidos_realizados")
    search_fields = ("nombre", "apellido", "email")
    ordering = ["apellido"]


class ProductoAdmin(admin.ModelAdmin):
    list_display = ("cerveceria", "nombre_comercial",
                    "variedad", "presentacion", "disponible")
    search_fields = ("cerveceria__nombre", "variedad",
                     "nombre_comercial", "cerveceria__pais")
    list_filter = ["cerveceria", "variedad", "presentacion"]
    ordering = ["cerveceria", "variedad"]


#Debo re-registrar a UserAdmin.
admin.site.unregister(User)

admin.site.register(User, UserAdmin)
admin.site.register(Presentacion)
admin.site.register(Cerveceria)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Pedido, PedidoAdmin)
