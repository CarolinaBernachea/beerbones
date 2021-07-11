from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from cerveceria.models import *
from django.contrib.auth.views import LoginView



class ContactoForm(forms.Form):
	nombre = forms.CharField(required = False)
	correo = forms.EmailField()
	asunto = forms.CharField()
	mensaje = forms.CharField(widget = forms.Textarea)


class RegistroForm(UserCreationForm):
    nombre = forms.CharField()
    apellido = forms.CharField()
    direccion = forms.CharField()
    telefono = forms.CharField()
    email = forms.EmailField()

    class Meta:
    	model = User
    	fields = ('username', 'password1', 'password2', "nombre",
    			"apellido", "direccion", "telefono", "email",)

    # Esta función checkea si ya existe el mail y si ya está en uso muestra un error al 
    # usuario en lugar de dar error 1062 y romperse la página.
    def clean_email(self):
    	email = self.cleaned_data.get('email')
    	for correo in Cliente.objects.all():
    		if correo.email == email:
    			raise forms.ValidationError("{} ya está en uso.".format(email))
    	return email
    		

# Formulario para el carrito
OPCION_CANTIDAD_PRODUCTOS = [(i, str(i)) for i in range(1, 21)]

class AgregarAlCarritoForm(forms.Form):
    cantidad = forms.TypedChoiceField (choices = OPCION_CANTIDAD_PRODUCTOS,
                                        coerce = int)
    override = forms.BooleanField(required = False,
                                   initial = False,
                                    widget = forms.HiddenInput)


class CrearPedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['cliente']