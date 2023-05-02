from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import *
from .models import *
from django.utils import timezone
from django.contrib.auth.decorators import login_required
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

@login_required
def tasks(request):

    tasks=Task.objects.filter(user=request.user, datecompleted__isnull= True)

    return render(request, 'tasks.html', {
        'tasks':tasks
    })


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

@login_required
def create_task(request):

    if request.method == 'GET':
        return render(request, 'create_task.html', {
            'form':  TaskForm
        })
    else:
        try:
            # carga el formulario con la informacion que llega por post
            form = TaskForm(request.POST)
            # guardamos la data en una variable, commit false sirve para guardar datos en variables sin enviarlos a la base de datos
            new_task = form.save(commit=False)
            # en el user de la variable almacenamos el usuario que viene por request, es decir, el usuario que hizo la query
            new_task.user = request.user
            new_task.save()  # ahora si lo guardamos en la base de datos
            return redirect('tasks')
        except:
            return render(request, 'create_task.html', {
                'form': TaskForm,
                'error': 'Please provide valide data'
            })

@login_required
def task_detail(request,task_id): 
    
    if request.method == 'GET':
        task= get_object_or_404(Task, pk=task_id, user=request.user)#si la consulta sale mal no tumba todo el servidor, sino que arroja un 404
        form= TaskForm(instance=task) #carga el formulario con la data almacenada en la variable task
        return render(request, 'task_detail.html', {
            'task': task,
            'form': form
        })
    else:
        try:
            task= get_object_or_404(Task, pk=task_id, user=request.user)#obtiene la tarea, ademas filtra por el usuario current session
            TaskForm(request.POST, instance=task)#carga el formulario con la nueva data
            form.save()#lo guarda en la bbdd remplazazndo la info anterior
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html', {
            'task': task,
            'form': form,
            'error': 'Error updating'
        })

@login_required
def complete_task(request, task_id):
    task= get_object_or_404(Task, pk=task_id, user= request.user)
    if request.method == 'POST':
        task.datecompleted = timezone.now() #si la fecha de completada no es null, significa completa
        task.save()
        return redirect('tasks')

@login_required
def delete_task(request, task_id):
    task= get_object_or_404(Task, pk=task_id, user= request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')
    
def tasks_completed(request):
    tasks= Task.objects.filter(user=request.user, datecompleted__isnull= False).order_by('-datecompleted')
    return render(request, 'tasks.html', {'tasks': tasks})