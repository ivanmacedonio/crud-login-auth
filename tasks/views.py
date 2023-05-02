from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
# Create your views here.


def home(request):
    return render(request, 'home.html')


def signup(request):

    if request.method == 'GET':  # por defecto la informacion llega por GET, pues retorna el html mediante GET
        return render(request, 'signup.html', {
            'form': UserCreationForm
        })

    else:
        if request.POST['password1'] == request.POST['password2']:
            try:  # el try es que al haber un error no se tumbe la aplicacion entera

                user = User.objects.create_user(
                    username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)  # le creamos una cookie
                return redirect('tasks')

            except IntegrityError:

                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    'error': 'User Already exist!'
                })
        return render(request, 'signup.html', {
            'form': UserCreationForm,
            'error': 'Password dsnt match'
        })


def tasks(request):
    return render(request, 'tasks.html')


def signout(request):
    logout(request)  # cierra la cookie
    return redirect('home')


def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(  # authenticate compara los datos que llegan por post con los almacenados en la bbdd
            # para comprobar que el usuario existe
            request, username=request.POST['username'],
            password=request.POST['password'])
        if user is None:  # si el usuario no fue valido retorna None
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'Username or password incorrect'
            })
        else:
            # cargamos su cookie, pues el usuario es correcto
            login(request, user)
            return redirect('tasks')
