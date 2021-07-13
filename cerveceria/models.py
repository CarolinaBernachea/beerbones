from django.db import models
from django.db.models import Count
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Presentacion(models.Model):
    presentacion = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "Presentaciones"

    def __str__(self):
        return self.presentacion


class Cerveceria(models.Model):
    logo = models.ImageField(upload_to="logos_cervecerias")
    nombre = models.CharField(max_length=50)
    pais = models.CharField(max_length=50)
    ciudad = models.CharField(max_length=50)
    direccion = models.CharField(max_length=50)
    email = models.EmailField(verbose_name="e-mail", unique=True)
    sitio_web = models.URLField()

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ["nombre"]


class Producto(models.Model):
    nombre_comercial = models.CharField(max_length=50, blank=True)
    foto = models.ImageField(upload_to="fotos_productos")
    cerveceria = models.ForeignKey(Cerveceria, on_delete=models.CASCADE)
    variedad = models.CharField(max_length=50)
    presentacion = models.ForeignKey(Presentacion, on_delete=models.CASCADE)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(default="*Agregar descripción*")
    disponible = models.BooleanField(default=True)

    def __str__(self):
        if self.nombre_comercial == "":
            return '{} {} - {}'.format(self.cerveceria.nombre,
                   self.variedad, self.presentacion)
        else:
            return '{} {} - {}'.format(self.cerveceria.nombre,
                   self.nombre_comercial, self.presentacion)

    class Meta:
        ordering = ["cerveceria", "-disponible", "variedad", "nombre_comercial"]


class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    direccion = models.CharField(max_length=50)
    telefono = models.CharField(max_length=15)
    email = models.EmailField(verbose_name="e-mail", unique=True)

    def __str__(self):
        return '{} {}'.format(self.nombre, self.apellido)
      
    # la funcion hace una consulta a la BD para contar los pedidos por cliente
    def pedidos_realizados(self):
        consulta = Cliente.objects.filter(
            pk=self.id).annotate(contar=Count("pedido"))
        return consulta[0].contar

 
# Esta función es para sincronizar create() y save() de 'Cliente' con el create() y save() de 'User' y registrar ambos a la vez.

@receiver(post_save, sender = User)
def create_user_cliente(sender, instance, created, **kwargs):
    if created:
        Cliente.objects.create(user = instance)
    instance.cliente.save()


class Pedido(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    pagado = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

    def pedido_id(self):
        return "Pedido " + str(self.id)

    def get_costo_total(self):
        return sum(item.get_costo() for item in self.items.all())


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, related_name='item_pedido',
                                on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default = 1)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return str(self.id)

    def get_costo(self):
        return self.precio * self.cantidad
