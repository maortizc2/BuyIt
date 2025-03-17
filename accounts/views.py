from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from .forms import UserRegisterForm

def register_view(request):
    """Vista para registrar un nuevo usuario."""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            # Guardar el usuario, pero primero se encripta la contraseña
            user = form.save(commit=False)
            raw_password = form.cleaned_data['password']
            user.set_password(raw_password)
            user.save()

            messages.success(request, '¡Registro exitoso! Ya puedes iniciar sesión.')
            return redirect('home')
    else:
        form = UserRegisterForm()
    
    context = {'form': form}
    return render(request, 'accounts/register.html', context)


def login_view(request):
    """Vista para iniciar sesión."""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Has iniciado sesión exitosamente.')
            return redirect('home')  # Redirecciona a tu página principal o donde quieras
        else:
            messages.error(request, 'Credenciales inválidas. Inténtalo de nuevo.')
            return redirect('accounts:login')
    else:
        return render(request, 'accounts/login.html')


def logout_view(request):
    """Vista para cerrar sesión."""
    logout(request)
    messages.info(request, 'Has cerrado sesión.')
    return redirect('home')
